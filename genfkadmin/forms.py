from django import forms
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from genfkadmin import FIELD_ID_FORMAT, GENERIC_FIELD_NAME
from genfkadmin.fields import GenericFKField


class GenericFKModelForm(forms.ModelForm):
    """
    A ModelForm that automatically replaces the content type and foreign key
    fields of GenericForeignKeys with a single input supplies options for all
    the models with GenericRelations.
    """

    def __init__(self, *args, filter_callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.generic_fields = {}

        # private_fields has GenericForeignKeys, so we check for those here
        # and inject a fake field into the form. We also remove the
        # content_type and foreign_key fields if they exist on the declared
        # fields of the form so that we only have the generic field.
        for field in self._meta.model._meta.private_fields:
            if isinstance(field, GenericForeignKey):
                # we must name the generic field something other than the
                # original name, because GenericForeignKey are editable=False
                # and won't be allowed in the form
                generic_field_name = GENERIC_FIELD_NAME.format(
                    field_name=field.name
                )
                self.generic_fields[generic_field_name] = {
                    "original_field_name": field.name,
                    "ct_field": field.ct_field,
                    "fk_field": field.fk_field,
                }
                self.fields.pop(field.ct_field, None)
                self.fields.pop(field.fk_field, None)
                self.fields[generic_field_name] = GenericFKField(
                    field.model,
                    filter_callback=filter_callback,
                    label=field.name,
                    help_text=(
                        field.help_text if hasattr(field, "help_text") else ""
                    ),  # drop when drop django 4.2
                )

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
