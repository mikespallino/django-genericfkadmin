from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=256)

    ct = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    ob = models.PositiveBigIntegerField()
    media = GenericForeignKey("ct", "ob")


class Book(models.Model):
    name = models.CharField(max_length=256)
    author = models.CharField(max_length=256)
    genre = GenericRelation(Genre)

    def __str__(self):
        return f"{self.name} by {self.author}"


class Movie(models.Model):
    name = models.CharField(max_length=256)
    director = models.CharField(max_length=256)
    genre = GenericRelation(Genre)

    def __str__(self):
        return f"{self.name} by {self.director}"
