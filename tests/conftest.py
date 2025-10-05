import django
import pytest


def pytest_configure():
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            },
        },
        SITE_ID=1,
        SECRET_KEY="not very secret in tests",
        USE_I18N=True,
        STATIC_URL="/static/",
        ROOT_URLCONF="tests.urls",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {
                    "debug": True,
                },
            },
        ],
        MIDDLEWARE=(
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ),
        INSTALLED_APPS=(
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django.contrib.staticfiles",
            "tests",
        ),
        PASSWORD_HASHERS=("django.contrib.auth.hashers.MD5PasswordHasher",),
    )

    django.setup()


@pytest.fixture
def pets():
    from tests.factories import (
        CatFactory,
        DogFactory,
        PetFactory,
        UserFactory,
    )

    owner1 = UserFactory(username="o1")
    owner2 = UserFactory(username="o2")
    owner3 = UserFactory(username="o3")

    dog1 = DogFactory()
    dog2 = DogFactory()

    cat1 = CatFactory()
    cat2 = CatFactory()

    pet1 = PetFactory(owner=owner1, content_object=dog1)
    pet2 = PetFactory(owner=owner2, content_object=dog2)
    pet3 = PetFactory(owner=owner3, content_object=cat1)
    pet4 = PetFactory(owner=owner1, content_object=cat2)

    return {
        "owners": [owner1, owner2, owner3],
        "dogs": [dog1, dog2],
        "cats": [cat1, cat2],
        "pets": [pet1, pet2, pet3, pet4],
    }
