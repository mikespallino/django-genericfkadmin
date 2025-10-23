from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Pet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.owner} owns {self.content_object}"

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class Animal(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        abstract = True


class Dog(Animal):
    tags = GenericRelation(Pet)


class Cat(Animal):
    tags = GenericRelation(Pet)


class Elephant(Animal):
    pass
