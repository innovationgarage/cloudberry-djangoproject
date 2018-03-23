from django_netjsonconfig.base.base import BaseModel, BaseConfig
from django_netjsonconfig.base.config import AbstractConfig, TemplatesVpnMixin, TemplatesThrough
from django_netjsonconfig.base.device import AbstractDevice
from django_netjsonconfig.base.tag import AbstractTaggedTemplate, AbstractTemplateTag
from django_netjsonconfig.base.template import AbstractTemplate
from django_netjsonconfig.base.vpn import AbstractVpn, AbstractVpnClient
from django.db import models
from taggit.managers import TaggableManager
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
import cloudberry_app.backends
import django_netjsonconfig.settings as app_settings
from jsonfield import JSONField
import collections
from django.utils.functional import lazy
from django.utils.module_loading import import_string
from model_utils import Choices
from model_utils.fields import StatusField
import hashlib
import importlib
from jsonschema import FormatChecker, validate
from jsonschema.exceptions import ValidationError as JsonSchemaError
from netjsonconfig.exceptions import ValidationError
import django.apps

class BackendedModelMixin(object):
    schema_prefix = "/cloudberry_app/schema"
    
    @classmethod
    def get_backends(cls, *arg, **kw):
        for item in app_settings.BACKENDS:
            yield ("%s/backend/%s" % (cls.schema_prefix, item[0]), item[1])
        try:
            Backend
        except:
            return
        for backend in Backend.objects.all():
            yield ("%s/dynamic/%s" % (cls.schema_prefix, backend.id), backend.name)    

    def get_context(self):
        return getattr(self, 'context', {})

    def get_templates(self):
        return []
    
    def get_backend_instance(self):
        kwargs = {'config': self.get_config(),
                  'context': self.get_context(),
                  'templates': self.get_templates()}
        if self.backend.startswith("%s/dynamic/" % self.schema_prefix):
            backend = Backend.objects.get(id=self.backend.split("/")[-1])
            backend.init_backend(**kwargs)
        elif self.backend.startswith("%s/backend/" % self.schema_prefix):
            backend_cls = import_string(self.backend.split("/")[-1])
            backend = backend_cls(**kwargs)
        else:
            raise Exception("Unknown backend path: %s" % self.backend)
        return backend

class TemplatedBackend(cloudberry_app.backends.TemplatedBackend):
    def __init__(self, *arg, **kw):
        pass

    init_backend = cloudberry_app.backends.TemplatedBackend.__init__
    
class Backend(BaseModel, BackendedModelMixin, TemplatedBackend):
    schema_prefix = "/cloudberry_app/schema/transform"

    backend = models.CharField(_('backend'),
                               choices=BackendedModelMixin.get_backends(),
                               blank=True,
                               max_length=128,
                               help_text=_('Select <a href="http://netjsonconfig.openwisp.org/en/'
                                           'stable/" target="_blank">netjsonconfig</a> backend'))
    schema = JSONField(_('schema'),
                       default=dict,
                       blank=True,
                       help_text=_('JSONSchema for the configuration'),
                       load_kwargs={'object_pairs_hook': collections.OrderedDict},
                       dump_kwargs={'indent': 4})
    transform = JSONField(_('transform'),
                       default=dict,
                       blank=True,
                       help_text=_('<a href="https://github.com/dvdln/jsonpath-object-transform">jsonpath-object-transform</a>'
                                   'to transform the schema to that of the back-end and/or template'),
                       load_kwargs={'object_pairs_hook': collections.OrderedDict},
                       dump_kwargs={'indent': 4})
    
    def _schema_add_foreign_keys(self, schema):
        schema = dict(schema)
        if 'definitions' not in schema:
            schema['definitions'] = {}
        def add_foreign_key(model, title):
            app_label, cls = model.rsplit(".", 1)
            model_cls = django.apps.apps.get_registered_model(app_label, cls)
            instances = model_cls.objects.all().order_by(title)
            schema['definitions']['fk__%s' % model.replace(".", "_")] = {
                'title': cls,
                'type': 'object',
                'options': {'enum_titles': [getattr(instance, title) for instance in instances]},
                'enum': [{'model': model, 'id': str(instance.id)}
                         for instance in instances]
            }
        add_foreign_key("cloudberry_app.Device", "name")
        add_foreign_key("django_x509.Ca", "name")
        add_foreign_key("django_x509.Cert", "name")
        return schema

    @property
    def extended_schema(self):
        return self._schema_add_foreign_keys(self.schema)
    
    def validate(self):
        try:
            validate(self.config, self.extended_schema, format_checker=FormatChecker())
        except JsonSchemaError as e:
            raise ValidationError(e)

    def extract_foreign_keys(self, config, model):
        if isinstance(config, (dict, collections.OrderedDict)):
            if config.get('model') == model:
                yield config.get('id')
                return
            for key, value in config.items():
                for fk in self.extract_foreign_keys(value, model):
                    yield fk
        if isinstance(config, (list, tuple)):
            for value in config:
                for fk in self.extract_foreign_keys(value, model):
                    yield fk
                    
class Config(BackendedModelMixin, BaseConfig):
    class Meta(BaseConfig.Meta):
        abstract = False

    devices = models.ManyToManyField('cloudberry_app.Device', related_name='configs')

    device = None
    backend = models.CharField(_('backend'),
                               choices=BackendedModelMixin.get_backends(),
                               blank=True,
                               max_length=128,
                               help_text=_('Select <a href="http://netjsonconfig.openwisp.org/en/'
                                           'stable/" target="_blank">netjsonconfig</a> backend'))

    def get_lowest_backend_instance(self, context):
        self.context = context
        obj = self.get_backend_instance()
        while hasattr(obj, 'get_backend_instance'):
            obj = obj.get_backend_instance()
        return obj
    
    def save(self, *arg, **kw):
        BaseConfig.save(self, *arg, **kw)

        backend = self.get_backend_instance()
        if hasattr(backend, "extract_foreign_keys"):
            self.devices.clear()
            for device in backend.extract_foreign_keys(self.config, 'cloudberry_app.models.Device'):
                self.devices.add(device)
    
class AbstractDevice2(AbstractDevice):
    # This whole class is a hack, to be able to override a @property
    # from AbstractDevice with a django CharField
    # Not sure why it doesn't work without this intermediate class...
    backend = None
    last_ip = None
    status = None
    
    class Meta(AbstractDevice.Meta):
        abstract = True

def model_to_dict(model):
    def mangle(value):
        if isinstance(value, (bool, type(None), str, int, float)):
            return value
        elif isinstance(value, models.Model):
            return {'model': "%s.%s" % (value._meta.app_label, value._meta.model_name),
                    'id': str(value.id)}
        else:
            return str(value)
    return {f.name: mangle(getattr(model, f.name))
            for f in model._meta.fields}
    
        
class FkLookup(object):
    def __getitem__(self, name):
        return FkLookupModel(name)
    
class FkLookupModel(object):
    def __init__(self, model):
        self.model = django.apps.apps.get_registered_model(*model.split("."))
        
    def __getitem__(self, id):
        return model_to_dict(self.model.objects.get(id=id))
        
class Device(AbstractDevice2, BackendedModelMixin):
    STATUS = Choices('modified', 'running', 'error')
    status = StatusField(help_text=_(
        'modified means the configuration is not applied yet; '
        'running means applied and running; '
        'error means the configuration caused issues and it was rolledback'
    ))
    last_ip = models.GenericIPAddressField(blank=True,
                                           null=True,
                                           help_text=_('indicates the last ip from which the '
                                                       'configuration was downloaded from '
                                                       '(except downloads from this page)'))

    backend = models.CharField(_('backend'),
                               choices=[("/cloudberry_app/schema/backend/%s" % item[0], item[1]) for item in app_settings.BACKENDS],
                               blank=True,
                               max_length=128,
                               help_text=_('Select <a href="http://netjsonconfig.openwisp.org/en/'
                                           'stable/" target="_blank">netjsonconfig</a> backend'))

    class Meta(AbstractDevice.Meta):
        abstract = False

    def get_config_list(self):
        return ", ".join([c.name for c in self.configs.all()])
    get_config_list.short_description = "Configurations"

    def get_config(self):
        return {}
    
    def get_templates(self):
        if not hasattr(self, 'configs'):
            return []
        return [
            c.get_lowest_backend_instance(self.get_context()).config
            for c in self.configs.all()]
    
    def get_context(self):
        return {'device': model_to_dict(self),
                'fk': FkLookup()}
    
    # The controller expects a single config object with the
    # methods defined below, so we synthesize it...

    def _has_config(self):
        return False

    @property
    def config(self):
        return self

    def generate(self):
        return self.get_backend_instance().generate()

    @property
    def checksum(self):
        config = self.generate().getvalue()
        return hashlib.md5(config).hexdigest()

    def json(self, dict=False, **kwargs):
        config = self.get_backend_instance().config
        if dict:
            return config
        return json.dumps(config, **kwargs)
