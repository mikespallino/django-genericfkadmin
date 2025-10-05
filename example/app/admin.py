from functools import partial

from app.models import Cat, Dog, Elephant, Pet
from django.contrib import admin

from genfkadmin.admin import GenericFKAdmin
from genfkadmin.forms import GenericFKModelForm


class PetAdminForm(GenericFKModelForm):

    class Meta:
        model = Pet
        fields = "__all__"


@admin.register(Pet)
class PetAdmin(GenericFKAdmin):
    form = PetAdminForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj:
            self.form = partial(
                PetAdminForm,
                filter_callback=lambda queryset: queryset.filter(
                    tags__owner=obj.owner
                ),
            )
        return super().get_form(request, obj=obj, change=change, **kwargs)


@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    pass


@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    pass


@admin.register(Elephant)
class ElephantAdmin(admin.ModelAdmin):
    pass
