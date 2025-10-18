from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class MarketingMaterial(models.Model):
    title = models.CharField()
    body = models.TextField()

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class EmailDeliveryMechanism(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    value = models.CharField()
    material = GenericRelation(MarketingMaterial)

    def __str__(self):
        return f"EmailDeliveryMechanism - {self.value} for {self.customer.name}"


class SMSDeliveryMechanism(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    value = models.CharField()
    material = GenericRelation(MarketingMaterial)

    def __str__(self):
        return f"SMSDeliveryMechanism - {self.value} for {self.customer.name}"


class PromotionalMaterial(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    title = models.CharField()
    body = models.TextField()
    material = models.ForeignKey(MarketingMaterial, on_delete=models.CASCADE)

    def __str__(self):
        return f"Promotional Material - {self.title} for {self.customer.name}"
