from netjsonconfig.backends.base.backend import BaseBackend
import jpot
import netjsonconfig
import cloudberry_app.models
from django.utils.module_loading import import_string

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
        return jpot.transform(self.config, self.model.transform)

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
        
