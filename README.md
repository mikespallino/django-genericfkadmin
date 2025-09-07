# Django GenericFKAdmin

Using `GenericForeignKey` in your Django models is cool, the default behavior of
Django Admin is not. This package allows you to replace the `content_type` and
`object_id` fields in your admin forms with a single input that is prefilled
with only the models related through `GenericRelation` fields.

## Setup

### Install

### Usage

Using this package is pretty simple. 

1. Create a subclass of `GenericFKModelForm` for your model.
2. Create a subclass of `GenericFKAdmin` for your model.
3. ???
4. Profit!

e.g. in your `admin.py`
```python
class PetAdminForm(GenericFKModelForm):

    class Meta:
        model = Pet
        fields = "__all__"


@admin.register(Pet)
class PetAdmin(GenericFKAdmin):
    form = PetAdminForm
```



A complete example django app exists in this repository at [here](/example)


## Roadmap
1. Implement a filtering callback to further restrict the set of options available in the selector
2. Stacked and Tabular Inline support.