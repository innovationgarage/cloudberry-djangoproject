import json
import import_export.admin
import import_export.resources
import import_export.fields
import import_export.widgets
import import_export.formats.base_formats
import tablib

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
