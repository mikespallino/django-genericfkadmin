import factory
from django.contrib.auth import get_user_model

from tests.models import Cat, Dog, Elephant, Pet


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
