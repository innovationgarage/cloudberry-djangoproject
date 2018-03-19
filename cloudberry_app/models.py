from django_netjsonconfig.base.base import BaseModel
from django_netjsonconfig.base.config import AbstractConfig, TemplatesVpnMixin, TemplatesThrough
from django_netjsonconfig.base.device import AbstractDevice
from django_netjsonconfig.base.tag import AbstractTaggedTemplate, AbstractTemplateTag
from django_netjsonconfig.base.template import AbstractTemplate
from django_netjsonconfig.base.vpn import AbstractVpn, AbstractVpnClient
from sortedm2m.fields import SortedManyToManyField
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
            yield ("/cloudberry_app/schema/backend/%s" % item[0], item[1])
        try:
            Backend
        except:
            return
        for backend in Backend.objects.all():
            yield ("/cloudberry_app/schema/dynamic/%s" % backend.id, backend.name)
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
        if self.backend.startswith("/cloudberry_app/schema/dynamic/"):
            return cloudberry_app.backends.TemplatedBackend
        elif self.backend.startswith("/cloudberry_app/schema/backend/"):
            return import_string(self.backend[len("/cloudberry_app/schema/backend/"):])
    
class Config(TemplatesVpnMixin, AbstractConfig):
    class Meta(AbstractConfig.Meta):
        abstract = False

    # def __init__(self,  *args, **kwargs):
    #     super(Config, self).__init__(*args, **kwargs)
    #     self._meta.get_field('backend').choices = self.get_backends()
    #     self._meta.get_field('backend').get_choices = self.get_backends
        
    device = models.OneToOneField('cloudberry_app.Device', on_delete=models.CASCADE)
    templates = SortedManyToManyField('cloudberry_app.Template',
                                      related_name='config_relations',
                                      verbose_name=_('templates'),
                                      base_class=TemplatesThrough,
                                      blank=True,
                                      help_text=_('configuration templates, applied from '
                                                  'first to last'))
    vpn = models.ManyToManyField('cloudberry_app.Vpn',
                                 through='cloudberry_app.VpnClient',
                                 related_name='vpn_relations',
                                 blank=True)
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

class Device(AbstractDevice):
    class Meta(AbstractDevice.Meta):
        abstract = False

class TemplateTag(AbstractTemplateTag):
    class Meta(AbstractTemplateTag.Meta):
        abstract = False

class TaggedTemplate(AbstractTaggedTemplate):
    tag = models.ForeignKey('cloudberry_app.TemplateTag',
                            related_name='%(app_label)s_%(class)s_items',
                            on_delete=models.CASCADE)
    class Meta(AbstractTaggedTemplate.Meta):
        abstract = False

class Template(AbstractTemplate):
    tags = TaggableManager(through='cloudberry_app.TaggedTemplate', blank=True,
                           help_text=_('A comma-separated list of template tags, may be used '
                                       'to ease auto configuration with specific settings (eg: '
                                       '4G, mesh, WDS, VPN, ecc.)'))
    vpn = models.ForeignKey('cloudberry_app.Vpn',
                            verbose_name=_('VPN'),
                            blank=True,
                            null=True,
                            on_delete=models.CASCADE)
    class Meta(AbstractTemplate.Meta):
        abstract = False

class VpnClient(AbstractVpnClient):
    config = models.ForeignKey('cloudberry_app.Config',
                               on_delete=models.CASCADE)
    vpn = models.ForeignKey('cloudberry_app.Vpn',
                            on_delete=models.CASCADE)
    cert = models.OneToOneField('django_x509.Cert',
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True)
    class Meta(AbstractVpnClient.Meta):
        abstract = False

class Vpn(AbstractVpn):
    ca = models.ForeignKey('django_x509.Ca', verbose_name=_('CA'), on_delete=models.CASCADE)
    cert = models.ForeignKey('django_x509.Cert',
                             verbose_name=_('x509 Certificate'),
                             help_text=_('leave blank to create automatically'),
                             blank=True,
                             null=True,
                             on_delete=models.CASCADE)
    class Meta(AbstractVpn.Meta):
        abstract = False
