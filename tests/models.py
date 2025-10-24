from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()


class Pet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )

    def __str__(self):
        return f"{self.owner} owns {self.content_object}"

    class Meta:
        app_label = "tests"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class Dog(models.Model):
    name = models.CharField(max_length=256)
    tags = GenericRelation(Pet)

    class Meta:
        app_label = "tests"

    def __str__(self):
        return f"Dog - {self.name}"


class Cat(models.Model):
    name = models.CharField(max_length=256)
    tags = GenericRelation(Pet)

    class Meta:
        app_label = "tests"

    def __str__(self):
        return f"Cat - {self.name}"


class Elephant(models.Model):
    name = models.CharField(max_length=256)


class Customer(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class MarketingMaterial(models.Model):
    title = models.CharField(max_length=256)
    body = models.TextField()

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    delivery_method = GenericForeignKey("content_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"Marketing Material - {self.title} for {self.customer.name}"


class DeliveryMechanism(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    value = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.value} for {self.customer.name}"

    class Meta:
        abstract = True


class EmailDeliveryMechanism(DeliveryMechanism):
    material = GenericRelation(MarketingMaterial)


class SMSDeliveryMechanism(DeliveryMechanism):
    material = GenericRelation(MarketingMaterial)
