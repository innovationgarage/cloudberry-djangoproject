from django.contrib import admin
from .models import *
from .widget import JsonSchemaWidget
import json

from django_netjsonconfig.base.admin import (AbstractConfigForm,
                                             AbstractConfigInline,
                                             AbstractDeviceAdmin,
                                             AbstractTemplateAdmin,
                                             AbstractVpnAdmin,
                                             AbstractVpnForm,
                                             BaseForm,
                                             BaseAdmin)

class ConfigForm(AbstractConfigForm):
    class Meta(AbstractConfigForm.Meta):
        model = Config
        widgets = {'config': JsonSchemaWidget(attrs={'data-options': json.dumps({
                                                         "theme": 'bootstrap2',
                                                         "disable_collapse": False,
                                                         "disable_edit_json": False,
                                                         "display_required_only": True
                                                     })})}

class TemplateForm(BaseForm):
    class Meta(BaseForm.Meta):
        model = Template

class TemplateAdmin(AbstractTemplateAdmin):
    form = TemplateForm

class VpnForm(AbstractVpnForm):
    class Meta(AbstractVpnForm.Meta):
        model = Vpn

class VpnAdmin(AbstractVpnAdmin):
    form = VpnForm


class ConfigInline(AbstractConfigInline):
    model = Config
    form = ConfigForm
    extra = 0

class DeviceAdmin(AbstractDeviceAdmin):
    inlines = [ConfigInline]

class BackendForm(BaseForm):
    class Meta(BaseForm.Meta):
        model = Backend
        exclude = []
        widgets = {'schema': JsonSchemaWidget(attrs={'data-schema': '/cloudberry_app/schema/meta',
                                                     'data-options': json.dumps({
                                                         "theme": 'bootstrap2',
                                                         "disable_collapse": False,
                                                         "disable_edit_json": False,
                                                         "display_required_only": True
                                                     })})}

class BackendAdmin(BaseAdmin):
    model = Backend
    form = BackendForm

admin.site.register(Backend, BackendAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(Vpn, VpnAdmin)
