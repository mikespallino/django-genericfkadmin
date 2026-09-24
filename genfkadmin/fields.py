import logging
from traceback import format_exc

from django import forms
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import OperationalError
from django.forms import ChoiceField, Field, models

from genfkadmin.helpers import get_gfk_value, get_model_instance_for_gfk_value

logger = logging.getLogger(__name__)


class GenericModelChoiceIterator(models.BaseChoiceIterator):
    """
    A BaseChoiceIterator to be used with GenericFKField that iterates the
    relation tree to get the querysets necessary to populate the form field
    choices. Returns the choices as an option group with labels of the app
    and model name and values of FIELD_ID_FORMAT for instances.
    """

    def __init__(self, field):
        self.relation_tree = field._model._meta._relation_tree
        self.filter_callback = field._filter_callback

    def get_querysets_from_relation_tree(self):
        for relation in self.relation_tree:
            if isinstance(relation, GenericRelation):
                try:
                    queryset = relation.model.objects.all()
                    if self.filter_callback and callable(self.filter_callback):
                        try:
                            queryset = self.filter_callback(queryset=queryset)
                        except Exception:
                            logging.warning(
                                f"Unable to filter queryset with callback: {format_exc()}"
                            )
                    yield relation, queryset
                except OperationalError:
                    # table doesn't exist yet
                    pass

    def __iter__(self):
        # generic relations are stored in _relation_tree, so we can grab
        # the models from those relations and develop a set of choices
        # for the select input. The value of the choice is a formatted string
        # FIELD_ID_FORMAT, that stores the necessary information to parse
        # back out in the form on save to grab the content_type_id and
        # object_id of the selected value.
        for relation, queryset in self.get_querysets_from_relation_tree():
            app_label = relation.model._meta.app_label
            app_label = app_label[0].upper() + app_label[1:]
            yield (
                f"{app_label} | {relation.model.__name__}",
                [self.choice(obj) for obj in queryset],
            )

    def __len__(self):
        """
        Override super to return len of all querysets
        """
        count = 0
        for relation, queryset in self.get_querysets_from_relation_tree():
            count += queryset.count()
        return count

    def __bool__(self):
        return True

    def choice(self, obj) -> tuple[str, str]:
        """
        Return model instance as FIELD_ID_FORMAT string and __str__ of model.
        """
        return (
            get_gfk_value(obj),
            str(obj),
        )


class GenericFKField(forms.ModelChoiceField):
    """
    A ModelChoiceField that generates it's set of choices based on the related
    models for the GenericForeignKey Relations.
    """

    iterator = GenericModelChoiceIterator

    def __init__(
        self,
        model,
        *args,
        required=True,
        widget=None,
        label=None,
        initial=None,
        help_text="",
        filter_callback=None,
        **kwargs,
    ):
        """
        Given a model and an optional, initialize the set of
        choices that should be available for this field.
        """
        self._model = model
        self._filter_callback = filter_callback
        Field.__init__(
            self,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            **kwargs,
        )
        self.widget.choices = self.choices

    def to_python(self, value):
        """
        Overrides super to parse gfk FIELD_ID_FORMAT and validate
        object exists.
        """
        if value in self.empty_values:
            return None
        self.validate_no_null_characters(value)
        try:
            return get_model_instance_for_gfk_value(value)
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )
        return value

    def __deepcopy__(self, memo):
        # skip super interaction with queryset
        return super(ChoiceField, self).__deepcopy__(memo)


__all__ = [
    "GenericFKField",
]
