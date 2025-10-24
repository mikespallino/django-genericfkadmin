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


@pytest.fixture
def admin_user():
    from tests.factories import UserFactory

    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture
def marketing_materials():
    from tests.factories import (
        CustomerFactory,
        EmailDeliveryMechanismFactory,
        MarketingMaterialFactory,
        SMSDeliveryMechanismFactory,
    )

    c1 = CustomerFactory()
    c2 = CustomerFactory()

    e1 = EmailDeliveryMechanismFactory(customer=c1)
    e2 = EmailDeliveryMechanismFactory(customer=c1)
    sms1 = SMSDeliveryMechanismFactory(customer=c1)
    sms2 = SMSDeliveryMechanismFactory(customer=c1)

    e3 = EmailDeliveryMechanismFactory(customer=c2)
    e4 = EmailDeliveryMechanismFactory(customer=c2)
    sms3 = SMSDeliveryMechanismFactory(customer=c2)
    sms4 = SMSDeliveryMechanismFactory(customer=c2)

    m1 = MarketingMaterialFactory(customer=c1, delivery_method=sms1)
    m2 = MarketingMaterialFactory(customer=c2, delivery_method=e3)

    return {
        "customer": {"c1": c1, "c2": c2},
        "email": {"e1": e1, "e2": e2, "e3": e3, "e4": e4},
        "sms": {"sms1": sms1, "sms2": sms2, "sms3": sms3, "sms4": sms4},
        "marketing_materials": {
            "m1": {"instance": m1, "options": [e1, e2, sms1, sms2]},
            "m2": {"instance": m2, "options": [e3, e4, sms3, sms4]},
        },
    }
