import json
import import_export.admin
import import_export.resources
import import_export.fields
import import_export.widgets
import import_export.formats.base_formats
import django_admin_ownership.models
import django.contrib.auth.models
import cloudberry_import_export

class UserResource(import_export.resources.ModelResource):
    class Meta:
        model =  django.contrib.auth.models.User
        exclude = ("password",)

    permissions = import_export.fields.Field(attribute='permissions', widget=import_export.widgets.ManyToManyWidget(django.contrib.auth.models.Permission))

class GroupResource(import_export.resources.ModelResource):
    class Meta:
        model =  django.contrib.auth.models.Group

    members = import_export.fields.Field(attribute='user_set', widget=import_export.widgets.ManyToManyWidget(django.contrib.auth.models.User))
    permissions = import_export.fields.Field(attribute='permissions', widget=import_export.widgets.ManyToManyWidget(django.contrib.auth.models.Permission))
        
class ConfigurationGroupResource(import_export.resources.ModelResource):
    class Meta:
        model =  django_admin_ownership.models.ConfigurationGroup

    read = import_export.fields.Field(attribute='read', widget=import_export.widgets.ManyToManyWidget(django.contrib.auth.models.Group))
    write = import_export.fields.Field(attribute='write', widget=import_export.widgets.ManyToManyWidget(django.contrib.auth.models.Group))

    def dehydrate_group(self, configuration_group):
        return configuration_group.group and configuration_group.group.id
        
