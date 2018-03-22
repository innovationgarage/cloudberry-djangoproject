from netjsonconfig.backends.base.backend import BaseBackend
import jpot
import netjsonconfig
import cloudberry_app.models
from django.utils.module_loading import import_string
import json

class TemplatedBackend(BaseBackend):
    def __init__(self, config=None, native=None, templates=None, context=None):
        self.templates = templates
        self.context = context
        self._model = None
        BaseBackend.__init__(self, config, native)

    @property
    def model(self):
        if self._model is None:
            assert (self.config_instance.backend.startswith("/cloudberry_app/schema/dynamic/")
                    or self.config_instance.backend.startswith("/cloudberry_app/schema/transform/dynamic/"))
            self._model = cloudberry_app.models.Backend.objects.get(
                id=self.config_instance.backend.split("/")[-1])
        return self._model

    @property
    def schema(self):
        return self.model.extended_schema

    def transformed(self):
        return jpot.transform(
            # FIXME: This gets rid of ordered dicts, see https://github.com/adriank/ObjectPath/issues/25
            json.loads(json.dumps({"config": self.config, "context": self.context})),
            self.model.transform,
            verbatim_str=True,
            path_engine=jpot.path_objectpath)
    
    def get_backend_instance(self):
        inst = self.model.backend_class(
            config=self.transformed(),
            templates=self.templates,
            context=self.context)
        inst.config_instance = self.model
        return inst

    def render(self, *arg, **kw):
        return self.get_backend_instance().render(*arg, **kw)
        
    def generate(self, *arg, **kw):
        return self.get_backend_instance().generate(*arg, **kw)
        
    def extract_foreign_keys(self, config, model):
        return self.model.extract_foreign_keys(config, model)
