import copy
from functools import partial

from django.contrib import admin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core import checks

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
        if self.fields:
            return self.__handle_fields(copy.deepcopy(self.fields))
        else:
            return self.__handle_auto_gen()

    def get_fieldsets(self, *args, **kwargs):
        """
        Overrides get_fieldsets to remove content_type and foreign_key fields
        for the GenericForeignKey and replaces them with the dynamic fields
        anywhere in the fieldsets declaration if it exists
        """
        if self.fieldsets:
            updated_fieldsets = copy.deepcopy(self.fieldsets)
            for fieldset_name, fieldset in updated_fieldsets:
                fieldset["fields"] = self.__handle_fields(
                    copy.deepcopy(fieldset["fields"])
                )
            return updated_fieldsets
        else:
            return [(None, {"fields": self.get_fields(*args, **kwargs)})]

    def __handle_fields(self, fields_to_update):
        origin_type = type(fields_to_update)
        fields_to_update = list(fields_to_update)
        for field, generic_related_fields in self.generic_fields.items():
            # first check for top level fields
            try:
                fields_to_update.remove(generic_related_fields["ct_field"])
                fields_to_update.remove(generic_related_fields["fk_field"])
                fields_to_update.append(field)
                # we've done it for these fields, no need to check tuples
                continue
            except ValueError:
                pass

            # then check each field individually to see if it's a tuple to
            # dive a layer deeper
            for idx, declared_field in enumerate(fields_to_update):
                if isinstance(declared_field, tuple):
                    try:
                        ct_idx = declared_field.index(
                            generic_related_fields["ct_field"]
                        )
                        new_field = tuple(
                            declared_field[0:ct_idx]
                            + declared_field[ct_idx + 1 :]
                        )

                        fk_idx = new_field.index(
                            generic_related_fields["fk_field"]
                        )

                        new_field = tuple(
                            new_field[0:fk_idx] + new_field[fk_idx + 1 :]
                        )

                        new_field = new_field + (field,)
                        fields_to_update[idx] = new_field
                    except ValueError:
                        pass
        return origin_type(fields_to_update)

    def __handle_auto_gen(self):
        # if we don't have fields generate them ourselves, including the
        # dynamic generic foreign key fields
        updated_fields_with_generic_keys = []
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
        Overrides get_form to return our subclassed GenericFKModelForm. Bypass
        any auto form generation by simply returning the form attribute.
        """
        return self.form

    def check(self, **kwargs):
        """
        Overrides check to inject checks about the typing of the form being
        used with this admin class to ensure the admin will run without
        crashing.
        """
        errors = super().check(**kwargs)
        if not self.form:
            errors.append(
                checks.Error(
                    "Admin form not overridden",
                    hint="Add a form attribute to the admin class with a form that subclasses GenericFKModelForm",
                    obj=self,
                    id="genfkadmin.E001",
                )
            )
        else:
            if not (
                isinstance(self.form, partial)
                or issubclass(self.form, GenericFKModelForm)
            ):
                errors.append(
                    checks.Error(
                        "Admin form is not the correct type",
                        hint="self.form must be subclass of GenericFKModelForm",
                        obj=self,
                        id="genfkadmin.E002",
                    )
                )
            elif isinstance(self.form, partial) and not issubclass(
                self.form.func, GenericFKModelForm
            ):
                errors.append(
                    checks.Error(
                        "Admin form partial is not the correct type",
                        hint="self.form.func must be subclass of GenericFKModelForm",
                        obj=self,
                        id="genfkadmin.E003",
                    )
                )
        return errors


__all__ = [
    "GenericFKAdmin",
]
