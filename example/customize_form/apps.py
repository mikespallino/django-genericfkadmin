from django.apps import AppConfig


class CustomizeFormConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customize_form"
