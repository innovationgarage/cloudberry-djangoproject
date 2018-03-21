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

class Backend(BaseModel):
    def get_backends(*arg, **kw):
        for item in app_settings.BACKENDS:
            yield ("/cloudberry_app/schema/transform/backend/%s" % item[0], item[1])
        try:
            Backend
        except:
            return
        for backend in Backend.objects.all():
            yield ("/cloudberry_app/schema/transform/dynamic/%s" % backend.id, backend.name)
    backend = models.CharField(_('backend'),
                               choices=get_backends(),
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

    @cached_property
    def backend_class(self):
        if self.backend.startswith("/cloudberry_app/schema/transform/dynamic/"):
            return cloudberry_app.backends.TemplatedBackend
        elif self.backend.startswith("/cloudberry_app/schema/transform/backend/"):
            return import_string(self.backend[len("/cloudberry_app/schema/transform/backend/"):])

   
    def _schema_add_foreign_keys(self, schema):
        schema = dict(schema)
        if 'definitions' not in schema:
            schema['definitions'] = {}
        devices = Device.objects.all().order_by('name')
        schema['definitions']['foreign_key__device'] = {
            'title': 'Device',
            'type': 'object',
            'options': {'enum_titles': [device.name for device in devices]},
            'enum': [{'model': 'cloudberry_app.models.Device', 'id': str(devices.id)}
                     for devices in devices]
        }
        return schema

    @property
    def extended_schema(self):
        return self._schema_add_foreign_keys(self.schema)

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
                    
class Config(BaseConfig):
    class Meta(BaseConfig.Meta):
        abstract = False

    devices = models.ManyToManyField('cloudberry_app.Device', related_name='configs')

    device = None
    def get_backends(*arg, **kw):
        for item in app_settings.BACKENDS:
            yield ("/cloudberry_app/schema/backend/%s" % item[0], item[1])
        for backend in Backend.objects.all():
            yield ("/cloudberry_app/schema/dynamic/%s" % backend.id, backend.name)
    backend = models.CharField(_('backend'),
                               choices=get_backends(),
                               blank=True,
                               max_length=128,
                               help_text=_('Select <a href="http://netjsonconfig.openwisp.org/en/'
                                           'stable/" target="_blank">netjsonconfig</a> backend'))

    @cached_property
    def backend_class(self):
        if self.backend.startswith("/cloudberry_app/schema/dynamic/"):
            return cloudberry_app.backends.TemplatedBackend
        elif self.backend.startswith("/cloudberry_app/schema/backend/"):
            return import_string(self.backend[len("/cloudberry_app/schema/backend/"):])

    def get_backend_instance(self, template_instances=None):
        inst = AbstractConfig.get_backend_instance(self, template_instances)
        inst.config_instance = self
        return inst

    def save(self, *arg, **kw):
        BaseConfig.save(self, *arg, **kw)

        backend = self.get_backend_instance()
        if hasattr(backend, "extract_foreign_keys"):
            self.devices.clear()
            for device in backend.extract_foreign_keys(self.config, 'cloudberry_app.models.Device'):
                self.devices.add(device)
    
class Device(AbstractDevice):
    class Meta(AbstractDevice.Meta):
        abstract = False

    def get_config_list(self):
        return ", ".join([c.name for c in self.configs.all()])
    get_config_list.short_description = "Configurations"

    @property
    def config(self):
        return self.configs.all()[0]

    
