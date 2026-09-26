Quickstart
==========

.. important::
   This package does not currently support any pagination controls. If you have a
   large number of related models, this is likely to have very poor performance.

After you've installed ``django-genfkadmin``, you're ready to use it in your
admin code. Simply replace your usage of ``django.contrib.admin.ModelAdmin``
with ``GenericFKAdmin``.

.. code-block:: python

    from genfkadmin.admin import GenericFKAdmin


    @admin.register(Pet)
    class PetAdmin(GenericFKAdmin):
        pass


-----------
Custom Form
-----------

If your admin is using a custom form all you need to do is have your form
subclass ``GenericFKModelForm`` like so.

.. code-block:: python

    class PetAdminForm(GenericFKModelForm):
        class Meta:
            model = Pet
            fields = "__all__"


    @admin.register(Pet)
    class PetAdmin(GenericFKAdmin):
        form = PetAdminForm
