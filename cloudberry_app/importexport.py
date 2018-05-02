import json
import import_export.admin
import import_export.resources
import import_export.fields
import import_export.widgets
import import_export.formats.base_formats
from .models import *

class JSON_FORMAT(import_export.formats.base_formats.JSON):
    def export_data(self, dataset, **kwargs):
        return json.dumps(dataset.dict, indent=2)

class InlinedManyToManyWidget(import_export.widgets.ManyToManyWidget):
    def __init__(self, resource=None, model=None, *args, **kwargs):
        self.resource = resource
        if resource and not model:
            model = resource.Meta.model
        super(InlinedManyToManyWidget, self).__init__(model, *args, **kwargs)

    def clean(self, value, row=None, *args, **kwargs):
        dataset = tablib.Dataset()
        dataset.dict = value
        res = self.resource().import_data(dataset)
        return [row.object_id for row in res.rows]

    def render(self, value, obj=None):
        return self.resource().export(value.all()).dict

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

    refers_devices = import_export.fields.Field(attribute='refers_devices', widget=InlinedManyToManyWidget(DeviceResource))
ConfigResource.fields['refers_configs'] = import_export.fields.Field(column_name='refers_configs', attribute='refers_configs', widget=InlinedManyToManyWidget(ConfigResource))

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
