import copy
from functools import partial
from typing import Callable

from django.contrib import admin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ImproperlyConfigured
from django.forms import ModelForm

from genfkadmin import GENERIC_FIELD_NAME
from genfkadmin.forms import GenericFKModelForm


class GenericFKAdmin(admin.ModelAdmin):
    """
    A ModelAdmin for use with a Model that utilizes GenericForeignKeys.
    """

    filter_callback: Callable = None

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
            if self.form and issubclass(self.form, GenericFKModelForm):
                # respect the GenericFKModelForm fields
                # there isn't a great way to maintain order here
                return [
                    *self.form.base_fields,
                    *self.get_readonly_fields(args[0], kwargs.get("obj")),
                ]
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
                ct_idx = fields_to_update.index(
                    generic_related_fields["ct_field"]
                )
                fk_idx = fields_to_update.index(
                    generic_related_fields["fk_field"]
                )

                fields_to_update.pop(ct_idx)
                fields_to_update.pop(
                    fk_idx - 1
                )  # above pop shrinks list so -1
                # figure out where the first generic field was and
                # insert the new field there accounting for removals
                new_idx = (
                    min(ct_idx, fk_idx)
                    if len(fields_to_update) >= min(ct_idx, fk_idx)
                    else len(fields_to_update)
                )
                fields_to_update.insert(new_idx, field)

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

                        # figure out where the first generic field was and
                        # insert the new field there accounting for removals
                        new_idx = (
                            min(ct_idx, fk_idx)
                            if len(new_field) >= min(ct_idx, fk_idx)
                            else len(new_field)
                        )
                        new_field = (
                            new_field[0:new_idx]
                            + (field,)
                            + new_field[new_idx + 1 :]
                        )
                        fields_to_update[idx] = new_field
                    except ValueError:
                        pass
        return origin_type(fields_to_update)

    def __handle_auto_gen(self):
        # if we don't have fields generate them ourselves, including the
        # dynamic generic foreign key fields
        updated_fields_with_generic_keys = []
        gen_fields_to_idx = dict()
        for field in self.model._meta.fields:
            if (
                not field.primary_key
                and field.name not in self.generic_related_fields
            ):
                updated_fields_with_generic_keys.append(field.name)
            elif field.name in self.generic_related_fields:
                # track where this field would have gone if we didn't skip it
                gen_fields_to_idx[field.name] = len(
                    updated_fields_with_generic_keys
                )
        for generic_field in self.generic_fields:
            # so we can figure out were we should put the generated field
            new_idx = min(
                gen_fields_to_idx[
                    self.generic_fields[generic_field]["ct_field"]
                ],
                gen_fields_to_idx[
                    self.generic_fields[generic_field]["fk_field"]
                ],
            )
            updated_fields_with_generic_keys.insert(new_idx, generic_field)
        return updated_fields_with_generic_keys

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Overrides get_form to ensure GenericFKModelForm is used instead of
        the default ModelForm. If we have a callback, supply it for the form
        so it can be used in the metaclass.
        """

        if not self.form or self.form == ModelForm:
            kwargs["form"] = GenericFKModelForm
        elif self.form and not issubclass(self.form, GenericFKModelForm):
            raise ImproperlyConfigured(
                "If providing form for GenericFKAdmin, form must subclass"
                " GenericFKModelForm"
            )
        else:
            kwargs["form"] = self.form

        if self.filter_callback:
            kwargs["form"].filter_callback = (
                partial(self.filter_callback, **{"obj": obj})
                if obj
                else self.filter_callback
            )
        return super().get_form(request, obj=obj, change=change, **kwargs)


__all__ = [
    "GenericFKAdmin",
]
