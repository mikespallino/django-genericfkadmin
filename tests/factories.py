import factory
from django.contrib.auth import get_user_model

from tests.models import (
    Cat,
    Customer,
    Dog,
    Elephant,
    EmailDeliveryMechanism,
    MarketingMaterial,
    Pet,
    SMSDeliveryMechanism,
)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()


class PetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pet


class DogFactory(factory.django.DjangoModelFactory):
    name = factory.faker.Faker("name")

    class Meta:
        model = Dog


class CatFactory(factory.django.DjangoModelFactory):
    name = factory.faker.Faker("name")

    class Meta:
        model = Cat


class ElephantFactory(factory.django.DjangoModelFactory):
    name = factory.faker.Faker("name")

    class Meta:
        model = Elephant


class CustomerFactory(factory.django.DjangoModelFactory):
    name = factory.faker.Faker("name")

    class Meta:
        model = Customer


class MarketingMaterialFactory(factory.django.DjangoModelFactory):
    title = factory.faker.Faker("text")
    body = factory.faker.Faker("text")

    class Meta:
        model = MarketingMaterial


class EmailDeliveryMechanismFactory(factory.django.DjangoModelFactory):
    value = factory.faker.Faker("email")

    class Meta:
        model = EmailDeliveryMechanism


class SMSDeliveryMechanismFactory(factory.django.DjangoModelFactory):
    value = factory.faker.Faker("phone_number")

    class Meta:
        model = SMSDeliveryMechanism
