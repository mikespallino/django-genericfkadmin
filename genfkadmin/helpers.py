from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from genfkadmin import FIELD_ID_FORMAT


def parse_gfk_value(value: str) -> tuple[ContentType, str]:
    """
    Given a value assumed to be of FIELD_ID_FORMAT, parse the string and return
    the ContentType and object id this value represents.
    """
    if not isinstance(value, str):
        raise ValueError("value should be a string")
    try:
        app_label, rest = value.split("$")
        model_name, dirty_id = rest.split("[")

        content_type = ContentType.objects.get(
            app_label=app_label, model=model_name
        )
        object_id = dirty_id.strip("[").strip("]")
    except (ValueError, TypeError, AttributeError):
        raise ValueError(
            f"Value is not GFK formatted: {value} {FIELD_ID_FORMAT}"
        )
    except ObjectDoesNotExist:
        raise ValueError(f"ContentType for value does not exist: {value}")

    return content_type, object_id


def get_model_instance_for_gfk_value(value: str) -> models.Model:
    """
    Given a value assumed to be of FIELD_ID_FORMAT, return the model
    instance the value represents.
    """
    if not isinstance(value, str):
        raise ValueError("value should be a string")
    content_type, object_id = parse_gfk_value(value)
    return content_type.get_object_for_this_type(pk=object_id)


def get_generic_fields(
    instance: models.Model,
) -> tuple[ContentType, str | int]:
    """
    Given a modal instance, return the ContentType and object id
    """
    if not issubclass(type(instance), models.Model):
        raise ValueError("instance should be a django model")
    content_type = ContentType.objects.get_for_model(instance)
    return content_type, instance.pk


def get_gfk_value(instance: models.Model) -> str:
    """
    Given a model instance, return the gfk string used in the form
    """
    if not issubclass(type(instance), models.Model):
        raise ValueError("instance should be a django model")
    return FIELD_ID_FORMAT.format(
        app_label=instance._meta.app_label,
        model_name=instance._meta.model_name,
        pk=instance.pk,
    )
