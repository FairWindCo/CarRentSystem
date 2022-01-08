from django.contrib import admin


class AddDynamicFieldMixin(admin.ModelAdmin):
    def get_fieldsets(self, request, obj=None):
        fs = super().get_fieldsets(request, obj)
        new_dynamic_fieldsets = getattr(self, 'dynamic_fieldsets', {})
        for set_name, field_def_list in new_dynamic_fieldsets.items():
            for field_name, field_def in field_def_list:
                # `gf.append(field_name)` results in multiple instances of the new fields
                fs = fs + ((set_name, {'fields': (field_name,)}),)
                # updating base_fields seems to have the same effect
                self.form.declared_fields.update({field_name: field_def})
        return fs

    def get_fields(self, request, obj=None):
        gf = super().get_fields(request, obj)
        new_dynamic_fields = getattr(self, 'dynamic_fields', [])
        # without updating get_fields, the admin_pages form will display w/o any new fields
        # without updating base_fields or declared_fields, django will throw an error:
        # django.core.exceptions.FieldError: Unknown field(s) (test) specified for MyModel.
        # Check fields/fieldsets/exclude attributes of class MyModelAdmin.
        for field_name, field_def in new_dynamic_fields:
            # `gf.append(field_name)` results in multiple instances of the new fields
            gf = gf + [field_name]
            # updating base_fields seems to have the same effect
            self.form.declared_fields.update({field_name: field_def})
        return gf