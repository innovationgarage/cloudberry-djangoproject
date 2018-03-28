from netjsonconfig.backends.base.backend import BaseBackend
import sakform
import netjsonconfig
import cloudberry_app.models
from django.utils.module_loading import import_string
import json

class TemplatedBackend(BaseBackend):
    backend_class = netjsonconfig.OpenWrt
    schema = {}
    transform = {}
    
    def __init__(self, config=None, native=None, templates=None, context=None):
        self.templates = templates
        self.context = context
        BaseBackend.__init__(self, config, native)

    def get_config(self):
        return sakform.transform(
            {"config": self.config, "context": self.context},
            self.transform)[0]
    
    def get_context(self):
        return self.context

    def get_templates(self):
        return self.templates

    def get_backend_instance(self):
        return self.backend_class(
            config=self.get_config(),
            templates=self.get_templates(),
            context=self.get_context())

    def render(self, *arg, **kw):
        return self.get_backend_instance().render(*arg, **kw)
        
    def generate(self, *arg, **kw):
        return self.get_backend_instance().generate(*arg, **kw)
