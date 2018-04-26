from django.contrib import admin
from .models import *
from .widget import JsonSchemaWidget
import json
from django.utils.translation import ugettext_lazy as _
import django.forms
import django.urls
from django.conf.urls import url
import sakform
import django.contrib
import django.shortcuts
import django.utils.html

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

import django.forms.models

class PreviewWidget(django.forms.widgets.Select):
    input_type = 'select'
    template_name = 'cloudberry_app/preview_widget.html'

class PreviewField(django.forms.models.ModelChoiceField):
    widget = PreviewWidget

class BackendForm(BaseForm):
    preview_config = PreviewField(queryset=Device.objects.all(), #filter(referred_in_configs__backend == ''),
                                  required=False)

    def is_valid(self):
        if '_go_preview_config' in self.data:
            return False
        BaseForm.is_valid(self)
    
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

    def preview(self, request, object_id=None):
        if object_id is None:
            obj = None
        else:
            obj = self.get_object(request, django.contrib.admin.utils.unquote(object_id), None)
            if obj is None:
                return self._get_obj_does_not_exist_redirect(request, self.model._meta, object_id)
        form = self.get_form(request, obj)(request.POST, request.FILES, instance=obj)
        device = cloudberry_app.models.Device.objects.get(id=form['preview_config'].value())

        config = device.referred_in_configs.get(backend=form.instance.get_url(Config.schema_prefix))
        transformed = sakform.transform(
            {"config": config.config, "context": device.get_context()},
            form.instance.transform)[0]
    
        django.contrib.messages.add_message(
            request,
            django.contrib.messages.INFO,
            django.utils.safestring.mark_safe('<div>Transformed config:</div><pre>%s</pre>' % django.utils.html.escape(json.dumps(transformed, indent=2))))
        
    @django.contrib.admin.options.csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.method == 'POST' and '_go_preview_config' in request.POST:
            self.preview(request, object_id)
        return BaseAdmin.changeform_view(self, request, object_id, form_url, extra_context)
    
    
admin.site.register(Config, ConfigAdmin)
admin.site.register(Backend, BackendAdmin)
admin.site.register(Device, DeviceAdmin)
