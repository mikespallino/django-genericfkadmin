from functools import partial

from django.contrib import admin
from filter.models import (
    Customer,
    EmailDeliveryMechanism,
    MarketingMaterial,
    PromotionalMaterial,
    SMSDeliveryMechanism,
)

from genfkadmin.admin import GenericFKAdmin
from genfkadmin.forms import GenericFKModelForm


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass


class MarketingMaterialAdminForm(GenericFKModelForm):

    class Meta:
        model = MarketingMaterial
        fields = "__all__"


@admin.register(MarketingMaterial)
class MarketingMaterialAdmin(GenericFKAdmin):
    form = MarketingMaterialAdminForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj:
            self.form = partial(
                MarketingMaterialAdminForm,
                filter_callback=lambda queryset: queryset.filter(
                    customer=obj.customer
                ),
            )
        else:
            # this is important, otherwise, 1. add -> 2. change -> 3. add
            # will use the filter on 2. in 3.
            self.form = MarketingMaterialAdminForm

        return super().get_form(request, obj=obj, change=change, **kwargs)


@admin.register(EmailDeliveryMechanism)
class EmailDeliveryMechanismAdmin(admin.ModelAdmin):
    pass


@admin.register(SMSDeliveryMechanism)
class SMSDeliveryMechanismAdmin(admin.ModelAdmin):
    pass


@admin.register(PromotionalMaterial)
class PromotionalMaterialAdmin(admin.ModelAdmin):
    pass
