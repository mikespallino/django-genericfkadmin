from functools import partial

from django.contrib import admin

from app.models import Pet, Dog, Cat

from django_genfkadmin.admin import GenericFKAdmin
from django_genfkadmin.forms import GenericFKModelForm


class PetAdminForm(GenericFKModelForm):

    class Meta:
        model = Pet
        fields = "__all__"


@admin.register(Pet)
class PetAdmin(GenericFKAdmin):
    form = PetAdminForm


@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    pass


@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    pass
