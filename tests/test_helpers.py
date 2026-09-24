import pytest
from django.contrib.contenttypes.models import ContentType

from genfkadmin import FIELD_ID_FORMAT
from genfkadmin.helpers import (
    get_generic_fields,
    get_gfk_value,
    get_model_instance_for_gfk_value,
    parse_gfk_value,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,exception",
    [
        (
            False,
            ValueError,
        ),
        (
            "not_right",
            ValueError,
        ),
        (
            FIELD_ID_FORMAT.format(
                app_label="fake_app", model_name="fake_model", pk="1"
            ),
            ValueError,
        ),
        (
            FIELD_ID_FORMAT.format(
                app_label="tests", model_name="marketingmaterial", pk="1"
            ),
            None,
        ),
    ],
    ids=["invalid_type", "invalid_string", "invalid_content_type", "valid"],
)
def test_parse_gfk_value(value, exception):
    if exception:
        with pytest.raises(exception):
            parse_gfk_value(value)
    else:
        assert parse_gfk_value(value)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,exception",
    [
        (
            False,
            ValueError,
        ),
        (
            "not_right",
            ValueError,
        ),
        (
            FIELD_ID_FORMAT.format(
                app_label="fake_app", model_name="fake_model", pk="1"
            ),
            ValueError,
        ),
        (
            FIELD_ID_FORMAT.format(
                app_label="tests", model_name="marketingmaterial", pk="1"
            ),
            None,
        ),
    ],
    ids=["invalid_type", "invalid_string", "invalid_content_type", "valid"],
)
def test_get_model_instance_for_gfk_value(
    value, exception, marketing_materials
):
    if exception:
        with pytest.raises(exception):
            get_model_instance_for_gfk_value(value)
    else:
        assert get_model_instance_for_gfk_value(value)


@pytest.mark.django_db
def test_get_generic_fields(pets):
    dog = pets["dogs"][0]
    content_type, object_id = get_generic_fields(dog)
    assert content_type == ContentType.objects.get(
        app_label="tests", model="dog"
    )
    assert object_id


@pytest.mark.django_db
def test_get_gfk_value(pets):
    dog = pets["dogs"][0]
    assert get_gfk_value(dog) == f"tests$dog[{dog.pk}]"
