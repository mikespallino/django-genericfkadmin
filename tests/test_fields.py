import pytest

from genfkadmin import FIELD_ID_FORMAT
from genfkadmin.fields import GenericFKField
from tests.factories import ElephantFactory
from tests.models import Pet


@pytest.mark.django_db
def test_field_has_choices(pets):
    field = GenericFKField(Pet)
    assert field.choices is not None


@pytest.mark.django_db
def test_field_choices_value_format(pets):
    expected_values = []
    for dog in pets["dogs"]:
        expected_values.append(
            FIELD_ID_FORMAT.format(
                app_label="tests", model_name="dog", pk=dog.pk
            )
        )
    for cat in pets["cats"]:
        expected_values.append(
            FIELD_ID_FORMAT.format(
                app_label="tests", model_name="cat", pk=cat.pk
            )
        )

    field = GenericFKField(Pet)
    for opt_group, choices in field.choices:
        for value, display_value in choices:
            assert value in expected_values


@pytest.mark.django_db
def test_field_choices_only_linked_models(pets):
    elephants = [ElephantFactory() for _ in range(3)]

    field = GenericFKField(Pet)
    elephant_choices = [
        FIELD_ID_FORMAT.format(
            app_label="tests", model_name="elephant", pk=el.pk
        )
        for el in elephants
    ]

    for value, display in field.choices:
        assert value not in elephant_choices
