# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.admin
import django.contrib.admin.utils
import django.db.models

def patch(obj):
    def patch(fn):
        is_classmethod = isinstance(fn, classmethod)
        if is_classmethod:
            fn = fn.__func__
        name = fn.__name__
        orig = getattr(obj, name, None)
        def wrapper(self, *arg, **kw):
            return fn(self, orig, *arg, **kw)
        if is_classmethod:
            wrapper = classmethod(wrapper)
        setattr(obj, name, wrapper)
    return patch

def row_access(Model, admin):
    AdminModel = type(admin)

    # print("row_access(%s, %s, %s)" % (Model, admin, getattr(Model, "_configuration_group", None)))

    if not hasattr(Model, "_configuration_group"):
        return

    if (    AdminModel.fields is not None
        and Model._configuration_group[0] not in AdminModel.fields):
        # Patch in an admin field if a fk has been patched in in the model.
        # Why as the second field? Because the first is often a name,
        # and we'd like to keep that... heuristics :P
        AdminModel.fields[1:1] = Model._configuration_group[:1]
    
    def _row_access_read_filter(Model, user, prefix=0):
        return {"__".join(Model._configuration_group[prefix:] + ["read", "user"]): user}

    def _row_access_write_filter(Model, user, prefix=0):
        return {"__".join(Model._configuration_group[prefix:] + ["write", "user"]): user}


    @patch(Model)
    @classmethod
    def objects_allowed_to(cls, orig, queryset, read=None, write=None, **kw):
        if read is not None and not read.is_superuser:
            queryset = queryset.filter(**_row_access_read_filter(Model, read, **kw))
        if write is not None and not write.is_superuser:
            queryset = queryset.filter(**_row_access_write_filter(Model, write, **kw))
        return queryset

    @patch(AdminModel)
    def get_queryset(self, orig, request):
        return Model.objects_allowed_to(orig(self, request), read=request.user)

    @patch(AdminModel)
    def has_add_permission(self, orig, request):
        return True

    @patch(Model)
    def allowed_to_change(self, orig, user):
        if user.is_superuser: return True
        obj1 = getattr(self, Model._configuration_group[0])
        return obj1.objects_allowed_to(type(obj1).objects.filter(id=obj1.id), write=user, prefix=1).count() > 0

    @patch(Model)
    def allowed_to_read(self, orig, user):
        if user.is_superuser: return True
        obj1 = getattr(self, Model._configuration_group[0])
        return obj1.objects_allowed_to(type(obj1).objects.filter(id=obj1.id), read=user, prefix=1).count() > 0

    @patch(AdminModel)
    def has_module_permission(self, orig, request):
        return self._has_change_permission(request) or self.has_view_permission(request) or self.has_delete_permission(request)
        
    @patch(AdminModel)
    def _has_change_permission(self, orig, request, obj=None):
        if obj is None: return True
        return obj.allowed_to_change(request.user)

    @patch(AdminModel)
    def has_change_permission(self, orig, request, obj=None):
        return self._has_change_permission(request, obj) or self.has_view_permission(request, obj)

    @patch(AdminModel)
    def has_delete_permission(self, orig, request, obj=None):
        if obj is None: return True
        return obj.allowed_to_change(request.user)
    
    @patch(AdminModel)
    def has_view_permission(self, orig, request, obj=None):
        if obj is None: return True
        return obj.allowed_to_read(request.user)

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

    @patch(Model)
    @classmethod
    def foreignkey_allowed_values(cls, orig, db_field, user):
        queryset = db_field.related_model.objects.all()
        if hasattr(db_field.related_model, "_configuration_group") and not user.is_superuser:
            queryset = db_field.related_model.objects_allowed_to(queryset, read=user)
        return queryset
        
    @patch(AdminModel)
    def formfield_for_foreignkey(self, orig, db_field, request, **kwargs):
        kwargs["queryset"] = db_field.model.foreignkey_allowed_values(db_field, request.user)
        return orig(self, db_field, request, **kwargs)

def add_row_access_to_all():
    for Model, admin_inst in django.contrib.admin.site._registry.items():
        row_access(Model, admin_inst)

