import pytest
from django import forms

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
