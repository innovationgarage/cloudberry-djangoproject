from django_netjsonconfig.base.base import BaseModel, BaseConfig
from django_netjsonconfig.base.config import AbstractConfig, TemplatesVpnMixin, TemplatesThrough
from django_netjsonconfig.base.device import AbstractDevice
from django_netjsonconfig.base.tag import AbstractTaggedTemplate, AbstractTemplateTag
from django_netjsonconfig.base.template import AbstractTemplate
from django_netjsonconfig.base.vpn import AbstractVpn, AbstractVpnClient
from django_netjsonconfig.validators import mac_address_validator
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
from django.utils.functional import lazy
from django.conf import settings
import django_x509.models
import django_admin_ownership.models
import cloudberry_app.fields
import cloudberry_app.transform

class Backend(BaseModel, cloudberry_app.backends.BackendedModelMixin, cloudberry_app.backends.TemplatedBackendModelMixin):
    group = models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                               on_delete=models.CASCADE)
    __configuration_group = ["group"]

    schema_prefix = "/cloudberry_app/schema/transform"

    backend = cloudberry_app.fields.DynamicTextListField(
        _('backend'),
        blank=True,
        max_length=128,
        help_text=_('Select <a href="http://netjsonconfig.openwisp.org/en/'
                    'stable/" target="_blank">netjsonconfig</a> backend'))
    backend.choices_fn = (lambda schema_prefix: (lambda: cloudberry_app.backends.BackendedModelMixin.get_backends(schema_prefix)))(schema_prefix)
    
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
            titles = [getattr(instance, title) for instance in instances]
            values = [{'model': model, 'id': str(instance.id)}
                      for instance in instances]
            if values:
                schema['definitions']['fk__%s' % model.replace(".", "_")] = {
                    'title': cls,
                    'type': 'object',
                    'options': {'enum_titles': titles},
                    'enum': values
                }
            else:
                schema['definitions']['fk__%s' % model.replace(".", "_")] = {
                    'title': cls,
                    'type': 'object'
                }
        add_foreign_key("cloudberry_app.Device", "name")
        add_foreign_key("cloudberry_app.Config", "name")
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
                    
class Config(cloudberry_app.backends.BackendedModelMixin, BaseConfig):
    group = models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                               on_delete=models.CASCADE)
    __configuration_group = ["group"]

    class Meta(BaseConfig.Meta):
        abstract = False

    refers_devices = models.ManyToManyField('cloudberry_app.Device', related_name='referred_in_configs')
    refers_configs = models.ManyToManyField('cloudberry_app.Config', related_name='referred_in_configs')

    device = None
    
    backend = cloudberry_app.fields.DynamicTextListField(
        _('backend'),
        blank=True,
        max_length=128,
        help_text=_('Select <a href="http://netjsonconfig.openwisp.org/en/'
                    'stable/" target="_blank">netjsonconfig</a> backend'))
    backend.choices_fn = lambda: cloudberry_app.backends.BackendedModelMixin.get_backends()

    def get_lowest_backend_instance(self, context):
        context = dict(context)
        context['referred_in_configs'] = [{'model': 'cloudberry_app.Config', 'id': str(instance.id)}
                                          for instance in self.referred_in_configs.all()]
        self.context = context
        obj = self.get_backend_instance()
        while hasattr(obj, 'get_backend_instance'):
            obj = obj.get_backend_instance()
        return obj
    
    def save(self, *arg, **kw):
        BaseConfig.save(self, *arg, **kw)

        backend = self.get_backend_instance()
        if hasattr(backend, "extract_foreign_keys"):
            self.refers_devices.clear()
            self.refers_configs.clear()
            for device in backend.extract_foreign_keys(self.config, 'cloudberry_app.Device'):
                self.refers_devices.add(device)

            for config in backend.extract_foreign_keys(self.config, 'cloudberry_app.Config'):
                self.refers_configs.add(config)
    
class AbstractDevice2(AbstractDevice):
    # This whole class is a hack, to be able to override a @property
    # from AbstractDevice with a django CharField
    # Not sure why it doesn't work without this intermediate class...
    backend = None
    last_ip = None
    status = None
    
    class Meta(AbstractDevice.Meta):
        abstract = True

        
class Device(AbstractDevice2, cloudberry_app.backends.BackendedModelMixin):
    group = models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                               on_delete=models.CASCADE)
    __configuration_group = ["group"]

    mac_address = models.CharField(max_length=17,
                                   unique=True,
                                   db_index=True,
                                   null=True,
                                   blank=True,
                                   validators=[mac_address_validator],
                                   help_text=_('primary mac address'))
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
                               choices=[(settings.ROOT + "/cloudberry_app/schema/backend/%s" % item[0], item[1]) for item in app_settings.BACKENDS],
                               blank=True,
                               max_length=128,
                               help_text=_('Select <a href="http://netjsonconfig.openwisp.org/en/'
                                           'stable/" target="_blank">netjsonconfig</a> backend'))

    class Meta(AbstractDevice.Meta):
        abstract = False

    def get_config_list(self):
        return ", ".join([c.name for c in self.referred_in_configs.all()])
    get_config_list.short_description = "Configurations"

    def get_config(self):
        return {}
    
    def get_templates(self):
        if not hasattr(self, 'referred_in_configs'):
            return []
        return [
            c.get_lowest_backend_instance(self.get_context()).config
            for c in self.referred_in_configs.all()]
    
    def get_context(self):
        return {'device': cloudberry_app.transform.model_to_dict(self),
                'fk': cloudberry_app.transform.FkLookup()}
    
    # The controller expects a single config object with the
    # methods defined below, so we synthesize it...

    def _has_config(self):
        return False

    def get_default_templates(self):
        return []
    
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


django_x509.models.Ca.add_to_class(
    'group', models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                               on_delete=models.CASCADE))

django_x509.models.Ca.__configuration_group = ["group"]
django_x509.models.Cert.__configuration_group = ["ca", "group"]
