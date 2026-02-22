import django
from django import forms
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import (
    ImproperlyConfigured,
)
from django.forms.forms import DeclarativeFieldsMetaclass
from django.forms.models import (
    ALL_FIELDS,
    BaseModelForm,
    ModelFormOptions,
    fields_for_model,
)

from genfkadmin import FIELD_ID_FORMAT, GENERIC_FIELD_NAME
from genfkadmin.fields import GenericFKField


class GenericFKModelFormMetaclass(DeclarativeFieldsMetaclass):
    """
    This is a rather annoying copy and paste of
        `django.forms.models.ModelFormMetaclass`
    that skips the missing fields check because we're injecting the
    custom _gfk field
    """

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        if bases == (BaseModelForm,):
            return new_class

        opts = new_class._meta = ModelFormOptions(
            getattr(new_class, "Meta", None)
        )

        # We check if a string was passed to `fields` or `exclude`,
        # which is likely to be a mistake where the user typed ('foo') instead
        # of ('foo',)
        for opt in ["fields", "exclude", "localized_fields"]:
            value = getattr(opts, opt)
            if isinstance(value, str) and value != ALL_FIELDS:
                msg = (
                    "%(model)s.Meta.%(opt)s cannot be a string. "
                    "Did you mean to type: ('%(value)s',)?"
                    % {
                        "model": new_class.__name__,
                        "opt": opt,
                        "value": value,
                    }
                )
                raise TypeError(msg)

        generic_fields = {}

        if opts.model:
            # If a model is defined, extract form fields from it.
            if opts.fields is None and opts.exclude is None:
                raise ImproperlyConfigured(
                    "Creating a ModelForm without either the 'fields' "
                    "attribute or the 'exclude' attribute is prohibited; form "
                    " %s needs updating." % name
                )

            if opts.fields == ALL_FIELDS:
                # Sentinel for fields_for_model to indicate "get the list of
                # fields from the model"
                opts.fields = None

            extra_kwargs = {}
            if django.VERSION[0] > 4:
                extra_kwargs["form_declared_fields"] = new_class.declared_fields

            fields = fields_for_model(
                opts.model,
                opts.fields,
                opts.exclude,
                opts.widgets,
                opts.formfield_callback,
                opts.localized_fields,
                opts.labels,
                opts.help_texts,
                opts.error_messages,
                opts.field_classes,
                # limit_choices_to will be applied during ModelForm.__init__().
                apply_limit_choices_to=False,
                **extra_kwargs,
            )

            # ==== SKIP THIS FIELD CHECK ====

            # make sure opts.fields doesn't specify an invalid field
            # none_model_fields = {k for k, v in fields.items() if not v}
            # missing_fields = none_model_fields.difference(
            #     new_class.declared_fields)
            # if missing_fields:
            #     message = "Unknown field(s) (%s) specified for %s"
            #     message %= (", ".join(missing_fields), opts.model.__name__)
            #     raise FieldError(message)

            # ==== SKIP THIS FIELD CHECK ====

            # Include all the other declared fields.
            fields.update(new_class.declared_fields)
        else:
            fields = new_class.declared_fields

        filter_callback = None
        for base in bases:
            if base == GenericFKModelForm:
                filter_callback = base.filter_callback

        # private_fields has GenericForeignKeys, so we check for those here
        # and inject a fake field into the form. We also remove the
        # content_type and foreign_key fields if they exist on the declared
        # fields of the form so that we only have the generic field.
        for field in new_class._meta.model._meta.private_fields:
            if isinstance(field, GenericForeignKey):
                # we must name the generic field something other than the
                # original name, because GenericForeignKey are
                # editable=False and won't be allowed in the form
                generic_field_name = GENERIC_FIELD_NAME.format(
                    field_name=field.name
                )
                generic_fields[generic_field_name] = {
                    "original_field_name": field.name,
                    "ct_field": field.ct_field,
                    "fk_field": field.fk_field,
                }
                fields.pop(field.ct_field, None)
                fields.pop(field.fk_field, None)
                display_name = " ".join(
                    [p[0].upper() + p[1:] for p in field.name.split("_")]
                )
                fields[generic_field_name] = GenericFKField(
                    field.model,
                    filter_callback=filter_callback,
                    label=display_name,
                    help_text=(
                        field.help_text if hasattr(field, "help_text") else ""
                    ),  # drop when drop django 4.2
                )

        new_class.base_fields = fields
        new_class.generic_fields = generic_fields

        return new_class


class GenericFKModelForm(
    forms.BaseModelForm, metaclass=GenericFKModelFormMetaclass
):
    """
    A ModelForm that automatically replaces the content type and foreign key
    fields of GenericForeignKeys with a single input supplies options for all
    the models with GenericRelations.
    """

    filter_callback = None

    def get_initial_for_field(self, field, field_name):
        # generate the initial value for any of the generic fields so that
        # the correct choice is auto selected
        if field_name in self.generic_fields:
            target_instance = getattr(
                self.instance,
                self.generic_fields[field_name]["original_field_name"],
            )
            if target_instance:
                return FIELD_ID_FORMAT.format(
                    app_label=target_instance._meta.app_label,
                    model_name=target_instance._meta.model_name,
                    pk=target_instance.pk,
                )
        return super().get_initial_for_field(field, field_name)

    def save(self, commit=True):
        instance = super().save(commit=commit)

        # for the generic fields, we parse the value out of FIELD_ID_FORMAT
        # which gives us the ability to query for the ContentType and get the
        # primary key of the related field. We use setattr to update these
        # values dynamically
        for generic_field, related_fields in self.generic_fields.items():
            target_model_instance = self.cleaned_data[generic_field]
            app_label, rest = target_model_instance.split("$")
            model_name, dirty_id = rest.split("[")

            content_type = ContentType.objects.get(
                app_label=app_label, model=model_name
            )
            object_id = dirty_id.strip("[").strip("]")

            setattr(instance, related_fields["ct_field"], content_type)
            setattr(instance, related_fields["fk_field"], object_id)

        return instance


__all__ = [
    "GenericFKModelForm",
]
