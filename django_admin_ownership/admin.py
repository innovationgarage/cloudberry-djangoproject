# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.admin
import django.contrib.auth.models
import django.contrib.auth.admin
import django_admin_ownership.models
import django_admin_ownership.importexport
import import_export.admin
import cloudberry_import_export
             
class ConfigurationGroupAdmin(import_export.admin.ImportExportMixin,
                              import_export.admin.ImportExportActionModelAdmin,
                              django.contrib.admin.ModelAdmin):
    resource_class = django_admin_ownership.importexport.ConfigurationGroupResource
    formats=(cloudberry_import_export.JSON_FORMAT,)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = []
        if not request.user.is_superuser:
            self.exclude.append('owner')
        return super(ConfigurationGroupAdmin, self).get_form(request, obj, **kwargs)
    
    
django.contrib.admin.site.register(
    django_admin_ownership.models.ConfigurationGroup,
    ConfigurationGroupAdmin)


class GroupAdmin(import_export.admin.ImportExportMixin,
                 import_export.admin.ImportExportActionModelAdmin,
                 django.contrib.auth.admin.GroupAdmin):
    resource_class = django_admin_ownership.importexport.GroupResource
    formats=(cloudberry_import_export.JSON_FORMAT,)

django.contrib.admin.site.unregister(django.contrib.auth.models.Group)
django.contrib.admin.site.register(django.contrib.auth.models.Group, GroupAdmin)


class UserAdmin(import_export.admin.ImportExportMixin,
                 import_export.admin.ImportExportActionModelAdmin,
                 django.contrib.auth.admin.UserAdmin):
    resource_class = django_admin_ownership.importexport.UserResource
    formats=(cloudberry_import_export.JSON_FORMAT,)

django.contrib.admin.site.unregister(django.contrib.auth.models.User)
django.contrib.admin.site.register(django.contrib.auth.models.User, UserAdmin)
