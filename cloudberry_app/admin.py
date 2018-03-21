from django.contrib import admin
from .models import *
from .widget import JsonSchemaWidget
import json
from django.utils.translation import ugettext_lazy as _

from django_netjsonconfig.base.admin import (AbstractConfigForm,
                                             AbstractConfigInline,
                                             AbstractDeviceAdmin,
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


class ConfigAdmin(BaseAdmin):
    verbose_name_plural = _('Device configuration details')
    readonly_fields = []
    fields = ['name',
              'backend',
              'config',
              'created',
              'modified']
    change_select_related = ()

    def get_queryset(self, request):
        qs = super(ConfigAdmin, self).get_queryset(request)
        return qs.select_related(*self.change_select_related)
    
    form = ConfigForm
    extra = 0
    
class DeviceAdmin(AbstractDeviceAdmin):
    inlines = []
    list_display =  AbstractDeviceAdmin.list_display + ['get_config_list']
    list_filter = ['created']
    list_select_related = ()
    readonly_fields = ['id_hex', 'get_config_list']
    fields = ['name',
              'mac_address',
              'id_hex',
              'key',
              'backend',
              'model',
              'os',
              'system',
              'created',
              'modified',
              'get_config_list']

class BackendForm(BaseForm):
    class Meta(BaseForm.Meta):
        model = Backend
        exclude = []
        widgets = {
            # 'schema': JsonSchemaWidget(attrs={'data-schema': '/cloudberry_app/schema/meta',
            #                                   'data-options': json.dumps({
            #                                       "theme": 'bootstrap2',
            #                                       "disable_collapse": False,
            #                                       "disable_edit_json": False,
            #                                       "display_required_only": True
            #                                   })}),
            # 'transform': JsonSchemaWidget(attrs={'data-schema-selector': '#id_backend',
            #                                      'data-options': json.dumps({
            #                                          "theme": 'bootstrap2',
            #                                          "disable_collapse": False,
            #                                          "disable_edit_json": False,
            #                                          "display_required_only": True
            #                                      })})
        }

class BackendAdmin(BaseAdmin):
    model = Backend
    form = BackendForm

admin.site.register(Config, ConfigAdmin)
admin.site.register(Backend, BackendAdmin)
admin.site.register(Device, DeviceAdmin)
