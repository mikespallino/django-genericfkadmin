from functools import partial
from unittest.mock import MagicMock

import pytest
from django import forms
from django.contrib import admin
from django.urls import reverse

from genfkadmin import FIELD_ID_FORMAT
from genfkadmin.admin import GenericFKAdmin
from genfkadmin.forms import GenericFKModelForm
from tests.factories import DogFactory, PetFactory
from tests.models import MarketingMaterial, Pet


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


@admin.register(Pet)
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


@pytest.mark.django_db
def test_admin_renders_changelist(client, admin_user):
    client.force_login(admin_user)

    dog1 = DogFactory()
    pet1 = PetFactory(owner=admin_user, content_object=dog1)

    url = reverse("admin:tests_pet_change", kwargs={"object_id": pet1.pk})

    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_renders_add(client, admin_user):
    client.force_login(admin_user)

    url = reverse("admin:tests_pet_add")

    response = client.get(url)
    assert response.status_code == 200


class MarketingMaterialAdminForm(GenericFKModelForm):

    class Meta:
        model = MarketingMaterial
        fields = "__all__"


@admin.register(MarketingMaterial)
class MarketingMaterialAdmin(GenericFKAdmin):
    form = MarketingMaterialAdminForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj:
            self.form = partial(
                MarketingMaterialAdminForm,
                filter_callback=lambda queryset: queryset.filter(
                    customer=obj.customer
                ),
            )
        else:
            # this is important, otherwise, 1. add -> 2. change -> 3. add
            # will use the filter on 2. in 3.
            self.form = MarketingMaterialAdminForm

        return super().get_form(request, obj=obj, change=change, **kwargs)


@pytest.mark.django_db
def test_admin_partial_subclass(marketing_materials):
    from django.contrib.admin import site

    admin = MarketingMaterialAdmin(MarketingMaterial, site)
    form = admin.get_form(
        MagicMock(),
        obj=marketing_materials["marketing_materials"]["m1"]["instance"],
    )()
    expected_choices = [
        FIELD_ID_FORMAT.format(
            app_label="tests",
            model_name=mechanism.__class__.__name__.lower(),
            pk=mechanism.pk,
        )
        for mechanism in marketing_materials["marketing_materials"]["m1"][
            "options"
        ]
    ]
    actual_choices = [
        value
        for optgroup, choices in form.fields["delivery_method_gfk"].choices
        for value, display_value in choices
    ]
    assert expected_choices == actual_choices


@pytest.mark.django_db
def test_admin_filtered_change_add_resets_filter(
    marketing_materials, client, admin_user
):
    client.force_login(admin_user)

    instance = marketing_materials["marketing_materials"]["m1"]["instance"]
    all_choices = [
        FIELD_ID_FORMAT.format(
            app_label="tests",
            model_name=mechanism.__class__.__name__.lower(),
            pk=mechanism.pk,
        )
        for mechanism in marketing_materials["marketing_materials"]["m1"][
            "options"
        ]
        + marketing_materials["marketing_materials"]["m2"]["options"]
    ]
    instance_choices = [
        FIELD_ID_FORMAT.format(
            app_label="tests",
            model_name=mechanism.__class__.__name__.lower(),
            pk=mechanism.pk,
        )
        for mechanism in marketing_materials["marketing_materials"]["m1"][
            "options"
        ]
    ]
    other_choices = [
        FIELD_ID_FORMAT.format(
            app_label="tests",
            model_name=mechanism.__class__.__name__.lower(),
            pk=mechanism.pk,
        )
        for mechanism in marketing_materials["marketing_materials"]["m2"][
            "options"
        ]
    ]

    url = reverse(
        "admin:tests_marketingmaterial_change",
        kwargs={"object_id": instance.pk},
    )
    response = client.get(url)
    assert response.status_code == 200

    for choice in instance_choices:
        assert (
            choice in response.content.decode()
        ), f"instance choice missing {choice}"
    for choice in other_choices:
        assert (
            choice not in response.content.decode()
        ), f"other choice included {choice}"

    url = reverse("admin:tests_marketingmaterial_add")
    response = client.get(url)
    assert response.status_code == 200

    for choice in all_choices:
        assert choice in response.content.decode(), f"choice missing {choice}"
