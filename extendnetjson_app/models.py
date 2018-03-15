from django_netjsonconfig.base.config import AbstractConfig, TemplatesVpnMixin, TemplatesThrough
from django_netjsonconfig.base.device import AbstractDevice
from django_netjsonconfig.base.tag import AbstractTaggedTemplate, AbstractTemplateTag
from django_netjsonconfig.base.template import AbstractTemplate
from django_netjsonconfig.base.vpn import AbstractVpn, AbstractVpnClient
from sortedm2m.fields import SortedManyToManyField
from django.db import models
from taggit.managers import TaggableManager
from django.utils.translation import ugettext_lazy as _


class Config(TemplatesVpnMixin, AbstractConfig):
    class Meta(AbstractConfig.Meta):
        abstract = False
    device = models.OneToOneField('extendnetjson_app.Device', on_delete=models.CASCADE)
    templates = SortedManyToManyField('extendnetjson_app.Template',
                                      related_name='config_relations',
                                      verbose_name=_('templates'),
                                      base_class=TemplatesThrough,
                                      blank=True,
                                      help_text=_('configuration templates, applied from '
                                                  'first to last'))
    vpn = models.ManyToManyField('extendnetjson_app.Vpn',
                                 through='extendnetjson_app.VpnClient',
                                 related_name='vpn_relations',
                                 blank=True)

class Device(AbstractDevice):
    class Meta(AbstractDevice.Meta):
        abstract = False

class TemplateTag(AbstractTemplateTag):
    class Meta(AbstractTemplateTag.Meta):
        abstract = False

class TaggedTemplate(AbstractTaggedTemplate):
    tag = models.ForeignKey('extendnetjson_app.TemplateTag',
                            related_name='%(app_label)s_%(class)s_items',
                            on_delete=models.CASCADE)
    class Meta(AbstractTaggedTemplate.Meta):
        abstract = False

class Template(AbstractTemplate):
    tags = TaggableManager(through='extendnetjson_app.TaggedTemplate', blank=True,
                           help_text=_('A comma-separated list of template tags, may be used '
                                       'to ease auto configuration with specific settings (eg: '
                                       '4G, mesh, WDS, VPN, ecc.)'))
    vpn = models.ForeignKey('extendnetjson_app.Vpn',
                            verbose_name=_('VPN'),
                            blank=True,
                            null=True,
                            on_delete=models.CASCADE)
    class Meta(AbstractTemplate.Meta):
        abstract = False

class VpnClient(AbstractVpnClient):
    config = models.ForeignKey('extendnetjson_app.Config',
                               on_delete=models.CASCADE)
    vpn = models.ForeignKey('extendnetjson_app.Vpn',
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
