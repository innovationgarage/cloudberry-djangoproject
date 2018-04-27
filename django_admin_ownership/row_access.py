# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.admin
import django.contrib.admin.utils

def patch(obj):
    def patch(fn):
        orig = getattr(obj, fn.__name__, None)
        def wrapper(self, *arg, **kw):
            return fn(self, orig, *arg, **kw)        
        setattr(obj, fn.__name__, wrapper)
    return patch

def row_access(Model, admin):
    if not hasattr(Model, "__configuration_group"):
        return

    AdminModel = type(admin)

    if Model.__configuration_group[0] not in AdminModel.fields:
        # Patch in an admin field if a fk has been patched in in the model.
        # Why as the second field? Because the first is often a name,
        # and we'd like to keep that... heuristics :P
        AdminModel.fields[1:1] = Model.__configuration_group[:1]
    
    def _row_access_read_filter(Model, request, prefix=0):
        return {"__".join(Model.__configuration_group[prefix:] + ["read", "user"]): request.user}

    def _row_access_write_filter(Model, request, prefix=0):
        return {"__".join(Model.__configuration_group[prefix:] + ["write", "user"]): request.user}
    
    @patch(AdminModel)
    def get_queryset(self, orig, request):
        if request.user.is_superuser:
            return orig(self, request)
        return orig(self, request).filter(**_row_access_read_filter(Model, request))

    @patch(AdminModel)
    def has_add_permission(self, orig, request):
        return True

    @patch(AdminModel)
    def _has_change_permission(self, orig, request, obj=None):
        if obj is None: return True
        if request.user.is_superuser: return True
        obj1 = getattr(obj, Model.__configuration_group[0])
        return type(obj1).objects.filter(id=obj1.id).filter(**_row_access_write_filter(Model, request, 1)).count() > 0

    @patch(AdminModel)
    def has_change_permission(self, orig, request, obj=None):
        return self._has_change_permission(request, obj) or self.has_view_permission(request, obj)

    @patch(AdminModel)
    def has_delete_permission(self, orig, request, obj=None):
        if obj is None: return True
        if request.user.is_superuser: return True
        obj1 = getattr(obj, Model.__configuration_group[0])
        return type(obj1).objects.filter(id=obj1.id).filter(**_row_access_write_filter(Model, request, 1)).count() > 0

    @patch(AdminModel)
    def has_view_permission(self, orig, request, obj=None):
        if obj is None: return True
        if request.user.is_superuser: return True
        obj1 = getattr(obj, Model.__configuration_group[0])
        return type(obj1).objects.filter(id=obj1.id).filter(**_row_access_read_filter(Model, request, 1)).count() > 0

    AdminModel._get_readonly_fields_recursion = False
    @patch(AdminModel)
    def get_readonly_fields(self, orig, request, obj=None):
        if not self._has_change_permission(request, obj):
            if self._get_readonly_fields_recursion:
                return []
            self._get_readonly_fields_recursion = True
            try:
                return django.contrib.admin.utils.flatten_fieldsets(self.get_fieldsets(request, obj))
            finally:
                self._get_readonly_fields_recursion = False                
        return orig(self, request, obj)

    @patch(AdminModel)
    def save_model(self, orig, request, obj, form, change):
        if not self._has_change_permission(request, obj):
            raise Exception("Action not allowed")
        orig(self, request, obj, form, change)

    @patch(AdminModel)
    def delete_model(self, orig, request, obj):
        if not self.has_delete_permission(request, obj):
            raise Exception("Action not allowed")
        orig(self, request, obj, form, change)

    @patch(AdminModel)
    def save_related(self, orig, request, form, formsets, change):
        if not self._has_change_permission(request, form.instance):
            raise Exception("Action not allowed")
        orig(self, request, form, formsets, change)

    @patch(AdminModel)
    def formfield_for_foreignkey(self, orig, db_field, request, **kwargs):
        if hasattr(db_field.related_model, "__configuration_group") and not request.user.is_superuser:
            kwargs["queryset"] = db_field.related_model.objects.all().filter(**_row_access_read_filter(db_field.related_model, request))
        return orig(self, db_field, request, **kwargs)

def add_row_access_to_all():
    for Model, admin_inst in django.contrib.admin.site._registry.items():
        row_access(Model, admin_inst)

