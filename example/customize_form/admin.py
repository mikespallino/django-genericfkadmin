from customize_form.models import Book, Genre, Movie
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import Textarea

from genfkadmin.admin import GenericFKAdmin
from genfkadmin.forms import GenericFKModelForm


class GenreAdminForm(GenericFKModelForm):

    class Meta:
        model = Genre
        fields = "__all__"
        widgets = {
            "name": Textarea(attrs={"cols": 80, "rows": 20}),
        }

    def clean_name(self):
        value = self.cleaned_data["name"]
        if value.lower() != value:
            raise ValidationError("name must be lowercase")
        return value


@admin.register(Genre)
class GenreAdmin(GenericFKAdmin):
    form = GenreAdminForm
    fields = ("name", ("ct", "ob"))


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    pass
