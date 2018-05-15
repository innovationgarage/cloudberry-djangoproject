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
import django_global_request.middleware
import tablib
import django.urls

class Backend(django_admin_ownership.models.GroupedConfigurationMixin, BaseModel, cloudberry_app.backends.BackendedModelMixin, cloudberry_app.backends.TemplatedBackendModelMixin):
    group = models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                               on_delete=models.CASCADE)
    _configuration_group = ["group"]

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
                       help_text=_('<a target="_blank" href="http://json-schema.org/">JSONSchema</a> for the configuration'),
                       load_kwargs={'object_pairs_hook': collections.OrderedDict},
                       dump_kwargs={'indent': 4})
    transform = JSONField(_('transform'),
                       default=dict,
                       blank=True,
                       help_text=_('<a target="_blank" href="https://innovationgarage.github.io/cloudberry-djangoproject/docs/backends.html">Transform</a> of the configuration'),
                       load_kwargs={'object_pairs_hook': collections.OrderedDict},
                       dump_kwargs={'indent': 4})
    
    def _add_foreign_key(self, schema, model, title):
        app_label, cls = model.rsplit(".", 1)
        model_cls = django.apps.apps.get_registered_model(app_label, cls)
        instances = model_cls.objects_allowed_to(
            model_cls.objects.all(),
            read=django_global_request.middleware.get_request().user
        ).order_by(title)
        titles = [getattr(instance, title) for instance in instances]
        values = ["fk://%s/%s" % (model, instance.id)
                  for instance in instances]
        if values:
            schema['definitions']['fk__%s' % model.replace(".", "__")] = {
                'title': cls,
                'type': 'string',
                'options': {'enum_titles': titles},
                'enum': values,
                'fk_model': model,
                'add_url': '/admin/%s/%s/add/?_to_field=id&_popup=1' % (app_label, model_cls._meta.model_name),
                'change_url': '/admin/%s/%s/__fk__/change/?_to_field=id&amp;_popup=1' % (app_label, model_cls._meta.model_name)
            }
        else:
            schema['definitions']['fk__%s' % model.replace(".", "__")] = {
                'title': cls,
                'type': 'object'
            }
            
    def _find_foreign_key(self, schema):
        # Finds {"$ref": "#/definitions/fk__cloudberry_app__Device"} schema items and yields
        # ("cloudberry_app.Device", {"$ref": "#/definitions/fk__cloudberry_app__Device"})
        if not hasattr(schema, 'items'): return
        if "$ref" in schema and schema["$ref"].startswith("#/definitions/fk__"):
            yield (schema["$ref"].split("#/definitions/fk__")[1].replace("__", "."), schema)
        for name, value in schema.items():
            if name == "$ref": continue
            for fk in self._find_foreign_key(value):
                yield fk
                
    def _schema_add_foreign_keys(self, schema):
        schema = dict(schema)
        if 'definitions' not in schema:
            schema['definitions'] = {}
        for model, data in list(self._find_foreign_key(schema)):
            self._add_foreign_key(schema, model, data.get("title", "name"))
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
        if isinstance(config, str):
            if config.startswith("fk://%s" % model):
                yield config.split("/")[-1]
        elif isinstance(config, (dict, collections.OrderedDict)):
            for key, value in config.items():
                for fk in self.extract_foreign_keys(value, model):
                    yield fk
        elif isinstance(config, (list, tuple)):
            for value in config:
                for fk in self.extract_foreign_keys(value, model):
                    yield fk
                    
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
    
    def save(self, *arg, **kw):
        super().save(*arg, **kw)

        backend = self.get_backend_instance()
        if hasattr(backend, "extract_foreign_keys"):
            self.refers_devices.clear()
            self.refers_configs.clear()
            for device in backend.extract_foreign_keys(self.config, 'cloudberry_app.Device'):
                self.refers_devices.add(device)

            for config in backend.extract_foreign_keys(self.config, 'cloudberry_app.Config'):
                self.refers_configs.add(config)

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


django_x509.models.Ca.add_to_class(
    'group', models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                               on_delete=models.CASCADE))

django_x509.models.Ca._configuration_group = ["group"]
django_x509.models.Cert._configuration_group = ["ca", "group"]
