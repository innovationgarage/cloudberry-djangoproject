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
import cloudberry_app.schema
import django_global_request.middleware
import tablib
import django.urls
from copy import deepcopy
import urllib.request
import json

class Backend(django_admin_ownership.models.GroupedConfigurationMixin, BaseModel, cloudberry_app.backends.BackendedModelMixin, cloudberry_app.backends.TemplatedBackendModelMixin):
    group = models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                               on_delete=models.CASCADE)
    _configuration_group = ["group"]

    schema_prefix = "/cloudberry_app/schema"

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
                       help_text=_('<a target="_blank" href="http://json-schema.org/">JSONSchema</a> for the configuration'),
                       load_kwargs={'object_pairs_hook': collections.OrderedDict},
                       dump_kwargs={'indent': 4})
    transform = JSONField(_('transform'),
                       default=dict,
                       blank=True,
                       help_text=_('<a target="_blank" href="https://innovationgarage.github.io/cloudberry-djangoproject/docs/backends.html">Transform</a> of the configuration'),
                       load_kwargs={'object_pairs_hook': collections.OrderedDict},
                       dump_kwargs={'indent': 4})
    
    @property
    def extended_schema(self):
        return cloudberry_app.schema.extend_schema(self.schema)
    
    def validate(self):
        try:
            validate(self.config, self.extended_schema, format_checker=FormatChecker())
        except JsonSchemaError as e:
            raise ValidationError(e)

class Config(django_admin_ownership.models.GroupedConfigurationMixin, cloudberry_app.backends.BackendedModelMixin, BaseConfig):
    group = models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                               on_delete=models.CASCADE)
    _configuration_group = ["group"]

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
        context['referred_in_configs'] = ["fk://cloudberry_app.Config/%s" % instance.id
                                          for instance in self.referred_in_configs.all()]
        self.context = context
        obj = self.get_backend_instance()
        while hasattr(obj, 'get_backend_instance'):
            obj = obj.get_backend_instance()
        return obj

    def get_config(self):
        config = super().get_config()
        for key in list(config.keys()):
            if key.startswith("__") and key.endswith("__"):
                del config[key]
        return config
    
    def save(self, *arg, **kw):
        super().save(*arg, **kw)

        backend = self.get_backend_instance()

        self.refers_devices.clear()
        self.refers_configs.clear()
        for model, fk in cloudberry_app.schema.extract_foreign_keys(self.config):
            if model == 'cloudberry_app.Device':
                self.refers_devices.add(fk)
            elif model == 'cloudberry_app.Config':
                self.refers_configs.add(fk)

    def get_device_list(self):
        return ", ".join([c.name for c in self.refers_devices.all()])
    get_device_list.short_description = "Devices"
                
class AbstractDevice2(AbstractDevice):
    # This whole class is a hack, to be able to override a @property
    # from AbstractDevice with a django CharField
    # Not sure why it doesn't work without this intermediate class...
    backend = None
    last_ip = None
    status = None
    
    class Meta(AbstractDevice.Meta):
        abstract = True

        
class Device(django_admin_ownership.models.GroupedConfigurationMixin, AbstractDevice2, cloudberry_app.backends.BackendedModelMixin):
    group = models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                               on_delete=models.CASCADE)
    _configuration_group = ["group"]

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
                               choices=[("/cloudberry_app/schema/backend/%s" % item[0], item[1]) for item in app_settings.BACKENDS],
                               default="/cloudberry_app/schema/backend/%s" % app_settings.BACKENDS[0][0],
                               blank=False,
                               max_length=128,
                               help_text=_('Select <a href="http://netjsonconfig.openwisp.org/en/'
                                           'stable/" target="_blank">netjsonconfig</a> backend'))

    os_image = cloudberry_app.fields.DynamicTextListField(
        _('os image'),
        blank=False,
        max_length=128,
        help_text=_('Select OS image'))
    def _get_os_images():
        try:
            with urllib.request.urlopen(settings.OPENWISP_DEVICE_IMAGE_URL) as f:
                return [(image, image) for image in json.load(f)["images"]]
        except Exception as e:
            print(e)
            return []
        
    os_image.choices_fn = _get_os_images
    
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

    @property
    def config(self):
        return self

    def _has_config(self):
        return True

    def get_default_templates(self):
        return []

    @property
    def checksum(self):
        config = self.generate().getvalue()
        return hashlib.md5(config).hexdigest()

    def json(self, dict=False, **kwargs):
        config = self.get_backend_instance().config
        if dict:
            return config
        return json.dumps(config, **kwargs)

