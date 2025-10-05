import copy
from functools import partial

from django.contrib import admin
from django.contrib.contenttypes.fields import GenericForeignKey

from genfkadmin import GENERIC_FIELD_NAME
from genfkadmin.forms import GenericFKModelForm


class GenericFKAdmin(admin.ModelAdmin):
    """
    A ModelAdmin for use with a Model that utilizes GenericForeignKeys.
    """

    form = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # store a mapping of our GenericForeignKeys to their content_type and
        # foreign_key fields
        self.generic_fields = {}
        self.generic_related_fields = set()
        for field in self.model._meta.private_fields:
            if isinstance(field, GenericForeignKey):
                self.generic_fields[
                    GENERIC_FIELD_NAME.format(field_name=field.name)
                ] = {
                    "ct_field": field.ct_field,
                    "fk_field": field.fk_field,
                }
                self.generic_related_fields.add(field.ct_field)
                self.generic_related_fields.add(field.fk_field)

    def get_fields(self, *args, **kwargs):
        """
        Overrides get_fields to remove content_type and foreign_key fields for
        the GenericForeignKey and replaces them with the dynamic fields.
        """
        updated_fields_with_generic_keys = []

        if self.fields:
            # if we have fields already make sure the content type and foreign
            # key fields aren't present and add our generic fields
            updated_fields_with_generic_keys = copy.deepcopy(self.fields)
            for field, generic_related_fields in self.generic_fields.items():
                try:
                    updated_fields_with_generic_keys.remove(
                        generic_related_fields["ct_field"]
                    )
                    updated_fields_with_generic_keys.remove(
                        generic_related_fields["fk_field"]
                    )
                    updated_fields_with_generic_keys.append(field)
                except ValueError:
                    pass
        else:
            # if we don't have fields generate them ourselves, including the
            # dynamic generic foreign key fields
            for field in self.model._meta.fields:
                if (
                    not field.primary_key
                    and field.name not in self.generic_related_fields
                ):
                    updated_fields_with_generic_keys.append(field.name)
            for generic_field in self.generic_fields:
                updated_fields_with_generic_keys.append(generic_field)
        return updated_fields_with_generic_keys

    def get_form(self, *args, **kwargs):
        """
        Overrides get_form to return our subclassed GenericFKModelForm.
        """
        # bypass any auto form generation by simply returning the form
        # attribute and do some gut checks to make sure we have an appropriate
        # form to use
        if not self.form:
            raise NotImplementedError(
                "Must define self.form that inherits from "
            )

        if not (
            isinstance(self.form, partial)
            or issubclass(self.form, GenericFKModelForm)
        ):
            raise NotImplementedError(
                "self.form must be subclass of GenericFKModelForm"
            )
        elif isinstance(self.form, partial) and not issubclass(
            self.form.func, GenericFKModelForm
        ):
            raise NotImplementedError(
                "self.form must be subclass of GenericFKModelForm"
            )
        return self.form


__all__ = [
    "GenericFKAdmin",
]
