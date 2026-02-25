from unittest.mock import MagicMock

import pytest
from django import forms
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from genfkadmin import FIELD_ID_FORMAT
from genfkadmin.admin import GenericFKAdmin
from genfkadmin.forms import GenericFKModelForm
from tests.factories import DogFactory, PetFactory
from tests.models import GenreA, GenreB, MarketingMaterial, Pet


class BadForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = "__all__"


class BadAdminConfiguration(GenericFKAdmin):
    form = BadForm


def test_admin_form_must_subclass():
    from django.contrib.admin import site

    admin = BadAdminConfiguration(Pet, site)
    with pytest.raises(ImproperlyConfigured) as ic:
        admin.get_form(MagicMock())

    assert ic.value.args[0] == (
        "If providing form for GenericFKAdmin, form must subclass GenericFKModelForm"
    )


@admin.register(Pet)
class GoodAdminConfiguration(GenericFKAdmin):
    pass


@pytest.mark.django_db
def test_admin_form_allows_form_subclass():
    from django.contrib.admin import site

    class PetAdminForm(GenericFKModelForm):
        class Meta:
            model = Pet
            fields = "__all__"

    admin = GoodAdminConfiguration(Pet, site)
    admin.form = PetAdminForm

    assert admin.get_form(MagicMock())


@pytest.mark.django_db
def test_admin_form_allows_form_subclass_with_filter_callback():
    from django.contrib.admin import site

    class PetAdminForm(GenericFKModelForm):
        class Meta:
            model = Pet
            fields = "__all__"

    admin = GoodAdminConfiguration(Pet, site)
    admin.filter_callback = lambda self, obj, queryset: queryset
    admin.form = PetAdminForm

    assert admin.get_form(MagicMock())


@pytest.mark.django_db
def test_admin_form_allows_form_subclass_with_other_fields():
    from django.contrib.admin import site

    class PetAdminForm(GenericFKModelForm):
        another_field = forms.CharField()

        class Meta:
            model = Pet
            fields = "__all__"

    admin = GoodAdminConfiguration(Pet, site)
    admin.filter_callback = lambda self, obj, queryset: queryset
    admin.form = PetAdminForm

    actual_fields = admin.get_fields(MagicMock())
    assert "another_field" in actual_fields
    assert "content_object_gfk" in actual_fields


def test_good_admin_check_returns_no_errors():
    from django.contrib.admin import site

    admin = GoodAdminConfiguration(Pet, site)
    errors = admin.check()

    assert not errors


def test_admin_stores_generic_fields():
    from django.contrib.admin import site

    admin = GoodAdminConfiguration(Pet, site)

    assert "content_object_gfk" in admin.generic_fields
    assert (
        admin.generic_fields["content_object_gfk"]["ct_field"]
        == "content_type"
    )
    assert (
        admin.generic_fields["content_object_gfk"]["fk_field"] == "object_id"
    )


def test_admin_stores_generic_related_fields():
    from django.contrib.admin import site

    admin = GoodAdminConfiguration(Pet, site)
    assert admin.generic_related_fields == {"content_type", "object_id"}


def test_admin_default_field_config_removes_generic_related_fields():
    from django.contrib.admin import site

    admin = GoodAdminConfiguration(Pet, site)
    fields = admin.get_fields(MagicMock())
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


@admin.register(MarketingMaterial)
class MarketingMaterialAdmin(GenericFKAdmin):
    def filter_callback(self, obj=None, queryset=None):
        if obj:
            return queryset.filter(customer=obj.customer)
        return queryset


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
        assert choice in response.content.decode(), (
            f"instance choice missing {choice}"
        )
    for choice in other_choices:
        assert choice not in response.content.decode(), (
            f"other choice included {choice}"
        )

    url = reverse("admin:tests_marketingmaterial_add")
    response = client.get(url)
    assert response.status_code == 200

    for choice in all_choices:
        assert choice in response.content.decode(), f"choice missing {choice}"


@admin.register(GenreA)
class GenreFieldsTupleAdmin(GenericFKAdmin):
    fields = ("name", ("ct", "ob"))


def test_admin_with_tuple_fields():
    from django.contrib.admin import site

    admin = GenreFieldsTupleAdmin(GenreA, site)
    fields = admin.get_fields()
    assert fields == ("name", ("media_gfk",))


@admin.register(GenreB)
class GenreFieldsetAdmin(GenericFKAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": ["name"],
            },
        ),
        (
            "Type",
            {
                "classes": ["collapse"],
                "fields": ["ct", "ob"],
            },
        ),
    ]


def test_admin_with_fieldsets():
    from django.contrib.admin import site

    admin = GenreFieldsetAdmin(GenreB, site)
    fields = admin.get_fieldsets()
    assert fields == [
        (None, {"fields": ["name"]}),
        (
            "Type",
            {
                "classes": ["collapse"],
                "fields": ["media_gfk"],
            },
        ),
    ]
