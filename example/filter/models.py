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
    title = models.CharField(max_length=256)
    body = models.TextField()

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"Marketing Material - {self.title} for {self.customer.name}"


class DeliveryMechanism(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    value = models.CharField()

    def __str__(self):
        return f"{self.value} for {self.customer.name}"

    class Meta:
        abstract = True


class EmailDeliveryMechanism(DeliveryMechanism):
    material = GenericRelation(MarketingMaterial)


class SMSDeliveryMechanism(DeliveryMechanism):
    material = GenericRelation(MarketingMaterial)


class PromotionalMaterial(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    title = models.CharField(max_length=256)
    body = models.TextField()
    material = models.ForeignKey(MarketingMaterial, on_delete=models.CASCADE)

    def __str__(self):
        return f"Promotional Material - {self.title} for {self.customer.name}"
