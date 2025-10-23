# Django GenericFKAdmin

Using `GenericForeignKey` in your Django models is cool, the default behavior of
Django Admin is not. This package allows you to replace the `content_type` and
`object_id` fields in your admin forms with a single input that is prefilled
with only the models related through `GenericRelation` fields.

## Setup

### Install

```shell
pip install django-genfkadmin
````

```shell
uv add django-genfkadmin
```

### Usage

Using this package is pretty simple.

1. Create a subclass of `GenericFKModelForm` for your model.
2. Create a subclass of `GenericFKAdmin` for your model.
3. ???
4. Profit!

e.g. in your `admin.py`
```python
from genfkadmin.admin import GenericFKAdmin
from genfkadmin.forms import GenericFKModelForm


class PetAdminForm(GenericFKModelForm):

    class Meta:
        model = Pet
        fields = "__all__"


@admin.register(Pet)
class PetAdmin(GenericFKAdmin):
    form = PetAdminForm
```

![example](docs/screenshots/example_base_admin.png)

#### Providing a `filter_callback`
If you want to further filter the queryset (perhaps by something related to
the parent instance of your model with `GenericForeignKey`) you can pass a
`partial` with a keyword argument of `filter_callback` as follows.

```python
@admin.register(MarketingMaterial)
class MarketingMaterialAdmin(GenericFKAdmin):
    form = MarketingMaterialAdminForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj:
            self.form = partial(
                MarketingMaterialAdminForm,
                filter_callback=lambda queryset: queryset.filter(customer=obj.customer),
            )
        else:
            # this is important, otherwise, 1. add -> 2. change -> 3. add
            # will use the filter on 2. in 3.
            self.form = MarketingMaterialAdmin
        return super().get_form(request, obj=obj, change=change, **kwargs)
```

Now when loading an existing `MarketingMaterial`, the `content_object` options are filtered by the chosen `Customer`
![example](docs/screenshots/example_filter_admin.png)

A complete example django app exists in this repository at [here](/example)


## Roadmap
1. Stacked and Tabular Inline support.
