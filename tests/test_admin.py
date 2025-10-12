from functools import partial
from unittest.mock import MagicMock

import pytest
from django import forms

from genfkadmin import FIELD_ID_FORMAT
from genfkadmin.admin import GenericFKAdmin
from genfkadmin.forms import GenericFKModelForm
from tests.models import Pet


class BadAdminConfiguration(GenericFKAdmin):
    pass


def test_admin_must_define_form():
    from django.contrib.admin import site

    with pytest.raises(NotImplementedError):
        admin = BadAdminConfiguration(Pet, site)
        admin.get_form()


class BadForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = "__all__"


def test_admin_form_must_subclass():
    from django.contrib.admin import site

    with pytest.raises(NotImplementedError):
        BadAdminConfiguration.form = BadForm
        admin = BadAdminConfiguration(Pet, site)
        admin.get_form()


def test_admin_form_partial_func_must_subclass():
    from django.contrib.admin import site

    with pytest.raises(NotImplementedError):
        BadAdminConfiguration.form = partial(BadForm)
        admin = BadAdminConfiguration(Pet, site)
        admin.get_form()


class GoodForm(GenericFKModelForm):

    class Meta:
        model = Pet
        fields = "__all__"


class GoodAdminConfiguration(GenericFKAdmin):
    form = GoodForm


def test_admin_stores_generic_fields():
    from django.contrib.admin import site

    admin = GoodAdminConfiguration(Pet, site)

    assert "content_object_gfk" in admin.generic_fields
    assert (
        admin.generic_fields["content_object_gfk"]["ct_field"] == "content_type"
    )
    assert admin.generic_fields["content_object_gfk"]["fk_field"] == "object_id"


def test_admin_stores_generic_related_fields():
    from django.contrib.admin import site

    admin = GoodAdminConfiguration(Pet, site)
    assert admin.generic_related_fields == {"content_type", "object_id"}


def test_admin_default_field_config_removes_generic_related_fields():
    from django.contrib.admin import site

    admin = GoodAdminConfiguration(Pet, site)
    fields = admin.get_fields()
    assert admin.generic_related_fields & set(fields) == set()


def test_admin_removes_generic_related_fields_when_fields_defined():
    from django.contrib.admin import site

    admin = GoodAdminConfiguration(Pet, site)
    admin.fields = ["owner", "content_type", "object_id"]
    fields = admin.get_fields()
    assert admin.generic_related_fields & set(fields) == set()


class GoodAdminPartialSubclassConfiguration(GenericFKAdmin):
    form = GoodForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj:
            self.form = partial(
                GoodForm,
                filter_callback=lambda queryset: queryset.filter(
                    tags__owner=obj.owner
                ),
            )
        return super().get_form(request, obj=obj, change=change, **kwargs)


@pytest.mark.django_db
def test_admin_partial_subclass(pets):
    from django.contrib.admin import site

    instance = pets["pets"][0]
    pets = [p.content_object for p in Pet.objects.filter(owner=instance.owner)]
    admin = GoodAdminPartialSubclassConfiguration(Pet, site)
    form = admin.get_form(MagicMock(), obj=instance)()
    expected_choices = [
        FIELD_ID_FORMAT.format(
            app_label="tests",
            model_name=pet.__class__.__name__.lower(),
            pk=pet.pk,
        )
        for pet in pets
    ]
    actual_choices = [v for v, dv in form.fields["content_object_gfk"].choices]
    assert expected_choices == actual_choices
