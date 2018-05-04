import json
import import_export.admin
import import_export.resources
import import_export.fields
import import_export.widgets
import import_export.formats.base_formats
import cloudberry_import_export
from .models import *

class DeviceResource(import_export.resources.ModelResource):
    class Meta:
        model = Device
        exclude = ("group",)

class ConfigResource(import_export.resources.ModelResource):
    class Meta:
        model = Config
        exclude = ("group",)
        
    def dehydrate_config(self, config):
        return config.config

    refers_devices = import_export.fields.Field(attribute='refers_devices', widget=cloudberry_import_export.InlinedManyToManyWidget(DeviceResource))
ConfigResource.fields['refers_configs'] = import_export.fields.Field(column_name='refers_configs', attribute='refers_configs', widget=cloudberry_import_export.InlinedManyToManyWidget(ConfigResource))

    # def dehydrate_refers_devices(self, config):
    #     return DeviceResource().export(config.refers_devices.all()).dict

    
class BackendResource(import_export.resources.ModelResource):
    class Meta:
        model = Backend
        exclude = ("group",)
 
    def dehydrate_schema(self, backend):
        return backend.schema

    def dehydrate_transform(self, backend):
        return backend.transform
