import pytest
from django.contrib.contenttypes.models import ContentType

from genfkadmin import FIELD_ID_FORMAT
from genfkadmin.fields import GenericFKField
from genfkadmin.forms import GenericFKModelForm
from tests.models import Cat, Dog, Pet


class PetAdminForm(GenericFKModelForm):

    class Meta:
        model = Pet
        fields = "__all__"


@pytest.mark.django_db
def test_form_detects_generic_fields():
    form = PetAdminForm()

    assert "content_object_gfk" in form.generic_fields
    assert (
        form.generic_fields["content_object_gfk"]["ct_field"] == "content_type"
    )
    assert form.generic_fields["content_object_gfk"]["fk_field"] == "object_id"


@pytest.mark.django_db
def test_form_removes_content_type_and_fk_fields():
    form = PetAdminForm()

    assert "content_object_gfk" in form.fields
    assert "content_type" not in form.fields
    assert "object_id" not in form.fields


@pytest.mark.django_db
def test_form_populates_initial_value(pets):
    instance = pets["pets"][0]
    dog = pets["dogs"][0]
    form = PetAdminForm(instance=instance)
    assert form.get_initial_for_field(
        GenericFKField, "content_object_gfk"
    ) == FIELD_ID_FORMAT.format(app_label="tests", model_name="dog", pk=dog.pk)


@pytest.mark.django_db
def test_form_save_updates_content_type_and_fk_fields(pets):
    instance = pets["pets"][0]
    assert instance.content_type == ContentType.objects.get_for_model(Dog)
    assert instance.content_object == pets["dogs"][0]

    cat = pets["cats"][0]
    form = PetAdminForm(
        data={
            "owner": instance.owner,
            "content_object_gfk": FIELD_ID_FORMAT.format(
                app_label="tests", model_name="cat", pk=cat.pk
            ),
        },
        instance=instance,
    )
    updated_instance = form.save()

    assert updated_instance.content_type == ContentType.objects.get_for_model(
        Cat
    )
    assert updated_instance.content_object == cat


@pytest.mark.django_db
def test_form_filter(pets):
    instance = pets["pets"][0]
    form = PetAdminForm(
        instance=instance,
        filter_callback=lambda queryset: queryset.filter(
            tags__owner=instance.owner
        ),
    )

    pets = [p.content_object for p in Pet.objects.filter(owner=instance.owner)]
    expected_choices = [
        FIELD_ID_FORMAT.format(
            app_label="tests",
            model_name=pet.__class__.__name__.lower(),
            pk=pet.pk,
        )
        for pet in pets
    ]
    actual_choices = [
        value
        for optgroup, choices in form.fields["content_object_gfk"].choices
        for value, display_value in choices
    ]

    assert expected_choices == actual_choices
