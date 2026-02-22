from django.contrib import admin
from django.db.models import QuerySet
from filter.models import (
    Customer,
    EmailDeliveryMechanism,
    MarketingMaterial,
    PromotionalMaterial,
    SMSDeliveryMechanism,
)

from genfkadmin.admin import GenericFKAdmin


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass


@admin.register(MarketingMaterial)
class MarketingMaterialAdmin(GenericFKAdmin):
    def filter_callback(
        self,
        queryset: QuerySet,
        obj: MarketingMaterial | None = None,
    ):
        if obj:
            return queryset.filter(customer=obj.customer)
        return queryset


@admin.register(EmailDeliveryMechanism)
class EmailDeliveryMechanismAdmin(admin.ModelAdmin):
    pass


@admin.register(SMSDeliveryMechanism)
class SMSDeliveryMechanismAdmin(admin.ModelAdmin):
    pass


@admin.register(PromotionalMaterial)
class PromotionalMaterialAdmin(admin.ModelAdmin):
    pass
