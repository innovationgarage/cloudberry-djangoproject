from netjsonconfig.backends.base.backend import BaseBackend
import sakform
import netjsonconfig
import cloudberry_app.models
from django.utils.module_loading import import_string
import json
from django.conf import settings
import django_netjsonconfig.settings as app_settings

class BackendedMixin(object):
    def get_backend_instance(self, template_instances=None):
        return self.backend_class(
            config=self.get_config(),
            templates=self.get_templates(),
            context=self.get_context())

    def render(self, *arg, **kw):
        return self.get_backend_instance().render(*arg, **kw)
        
    def generate(self, *arg, **kw):
        return self.get_backend_instance().generate(*arg, **kw)


class TemplatedBackend(BaseBackend, BackendedMixin):
    backend_class = netjsonconfig.OpenWrt
    schema = {}
    transform = {}
    
    def __init__(self, config=None, native=None, templates=None, context=None):
        self.templates = templates
        self.context = context
        BaseBackend.__init__(self, config, native)

    def get_config(self):
        return sakform.transform(
            {"config": self.config, "context": self.get_context()},
            self.transform)[0]
    
    def get_context(self):
        return self.context

    def get_templates(self):
        return self.templates


class TemplatedBackendModelMixin(TemplatedBackend):
    def __init__(self, *arg, **kw):
        pass

    init_backend = TemplatedBackend.__init__
    

class BackendedModelMixin(BackendedMixin):
    schema_prefix = "/cloudberry_app/schema"
    
    @classmethod
    def get_backends(cls, schema_prefix=None):
        if schema_prefix is None:
            schema_prefix = cls.schema_prefix
        schema_prefix = settings.ROOT + schema_prefix
        for item in app_settings.BACKENDS:
            yield ("%s/backend/%s" % (schema_prefix, item[0]), item[1])
        import cloudberry_app.models
        try:
            for backend in cloudberry_app.models.Backend.objects.all():
                yield ("%s/dynamic/%s" % (schema_prefix, backend.id), backend.name)    
        except Exception as e:
            return

    def get_url(self, schema_prefix = None):
        return "%s/dynamic/%s" % (settings.ROOT + (schema_prefix or self.schema_prefix), self.id)

    def get_context(self):
        return getattr(self, 'context', {})

    def get_templates(self):
        return []

    def backend_class(self, **kwargs):
        schema_prefix = settings.ROOT + self.schema_prefix
        if self.backend.startswith("%s/dynamic/" % schema_prefix):
            import cloudberry_app.models
            backend = cloudberry_app.models.Backend.objects.get(id=self.backend.split("/")[-1])
            backend.init_backend(**kwargs)
        elif self.backend.startswith("%s/backend/" % schema_prefix):
            backend_cls = import_string(self.backend.split("/")[-1])
            backend = backend_cls(**kwargs)
        else:
            raise Exception("Unknown backend path %s in %s" % (self.backend, type(self)))
        return backend
    
    def clean_netjsonconfig_backend(self, backend):
        pass
