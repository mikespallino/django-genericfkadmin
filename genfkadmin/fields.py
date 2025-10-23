import logging
from traceback import format_exc

from django import forms
from django.contrib.contenttypes.fields import GenericRelation

from genfkadmin import FIELD_ID_FORMAT

logger = logging.getLogger(__name__)


class GenericFKField(forms.ChoiceField):
    """
    A ChoiceField that generates it's set of choices based on the related
    models for the GenericForeignKey Relations.
    """

    def __init__(self, model, *args, filter_callback=None, **kwargs):
        """
        Given a model and an optional, initialize the set of
        choices that should be available for this field.
        """
        choices = []

        # generic relations are stored in _relation_tree, so we can grab
        # the models from those relations and develop a set of choices
        # for the select input. The value of the choice is a formatted string
        # FIELD_ID_FORMAT, that stores the necessary information to parse
        # back out in the form on save to grab the content_type_id and
        # object_id of the selected value.
        for relation in model._meta._relation_tree:
            if isinstance(relation, GenericRelation):
                queryset = relation.model.objects.all()
                if filter_callback and callable(filter_callback):
                    try:
                        queryset = filter_callback(queryset)
                    except Exception:
                        logging.warning(
                            f"Unable to filter queryset with callback: {format_exc()}"
                        )

                choices_for_model = [
                    (
                        FIELD_ID_FORMAT.format(
                            app_label=i._meta.app_label,
                            model_name=i._meta.model_name,
                            pk=i.pk,
                        ),
                        str(i),
                    )
                    for i in queryset
                ]

                app_label = relation.model._meta.app_label
                app_label = app_label[0].upper() + app_label[1:]
                choices.append(
                    (
                        f"{app_label} | {relation.model.__name__}",
                        choices_for_model,
                    )
                )

        super().__init__(
            *args,
            choices=choices,
            **kwargs,
        )


__all__ = [
    "GenericFKField",
]
