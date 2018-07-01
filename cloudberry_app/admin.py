from django.contrib import admin
import django.forms
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
import django.forms.models
import cloudberry_app.importexport
import import_export.admin
import cloudberry_import_export
import reversion
from django.conf import settings

from django_netjsonconfig.base.admin import (AbstractConfigForm,
                                             AbstractConfigInline,
                                             AbstractDeviceAdmin,
                                             BaseForm,
                                             BaseAdmin)


class ConfigForm(AbstractConfigForm):
    class Meta(AbstractConfigForm.Meta):
        model = Config
        widgets = {'config': JsonSchemaWidget(attrs={
            'data-schema-selector-base': settings.ROOT,
            'data-options': json.dumps({
                "theme": 'django',
                "iconlib": "fontawesome4",
                "disable_collapse": False,
                "disable_edit_json": False,
                "display_required_only": True
            })})}

class ConfigAdmin(import_export.admin.ImportExportMixin,
                  import_export.admin.ImportExportActionModelAdmin,
                  BaseAdmin,
                  reversion.admin.VersionAdmin):
    change_form_template = 'cloudberry_app/config_admin.html'
    formats=(cloudberry_import_export.JSON_FORMAT,)
    resource_class = cloudberry_app.importexport.ConfigResource
    verbose_name_plural = _('Device configuration details')
    readonly_fields = ['get_device_list']
    list_display =  ['name', 'backend', 'created', 'modified', 'get_device_list']
    fieldsets = (
        (None, {
            'classes': ('model-info',),
            'fields': ['created',
                       'modified',
                       'get_device_list']
        }),
        (None, {
            'fields': ['name',
                       'group',
                       'backend',
                       'config']
        })
    )
    change_select_related = ()

    def get_queryset(self, request):
        qs = super(ConfigAdmin, self).get_queryset(request)
        return qs.select_related(*self.change_select_related)
    
    form = ConfigForm
    extra = 0

class DeviceAdmin(import_export.admin.ImportExportMixin,
                  import_export.admin.ImportExportActionModelAdmin,
                  AbstractDeviceAdmin,
                  reversion.admin.VersionAdmin):
    change_form_template = 'cloudberry_app/device_admin.html'

    def get_extra_context(self, pk=None):
        ctx = AbstractDeviceAdmin.get_extra_context(self, pk)
        if pk:
            ctx['download_image_url'] = django.urls.reverse('cloudberry_app:download_device_image', kwargs={"device": pk})
        return ctx
    
    formats=(cloudberry_import_export.JSON_FORMAT,)
    resource_class = cloudberry_app.importexport.DeviceResource
    inlines = []
    list_display =  AbstractDeviceAdmin.list_display + ['get_config_list']
    list_filter = ['created']
    list_select_related = ()
    readonly_fields = ('id_hex', 'key', 'get_config_list')
    fields = None
    fieldsets = (
        (None, {
            'classes': ('model-info',),
            'fields': ['id_hex',
                       'key',
                       'created',
                       'modified',
                       'get_config_list']
        }),
        (None, {
            'fields': ['name',
                       'group']
        }),
        (None, {
            'fields': ['backend',
                       'os_image']
        }),
        (None, {
            'fields': [('mac_address',
                        'os'),
                       ('model',
                        'system')]
        })
    )

    # Override base class that 'hides' id_hex in add view, breaking fieldsets...
    def get_fields(self, request, obj=None):
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

    
class PreviewWidget(django.forms.widgets.Select):
    input_type = 'select'
    template_name = 'cloudberry_app/preview_widget.html'

class PreviewField(django.forms.models.ModelChoiceField):
    widget = PreviewWidget

class BackendForm(BaseForm):
    preview_config = PreviewField(queryset=Device.objects.all(), #filter(referred_in_configs__backend == ''),
                                  required=False, label='Preview transform using config')

    def __init__(self, *arg, **kw):
        BaseForm.__init__(self, *arg, **kw)
        self.fields['preview_config'].queryset = self.fields['preview_config'].queryset.filter(
            referred_in_configs__backend=self.instance.get_url(Config.schema_prefix))
    
    def is_valid(self):
        if '_go_preview_config' in self.data:
            return False
        return BaseForm.is_valid(self)
    
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
        
class BackendAdmin(import_export.admin.ImportExportMixin,
                   import_export.admin.ImportExportActionModelAdmin,
                   BaseAdmin,
                   reversion.admin.VersionAdmin):
    change_form_template = 'cloudberry_app/change_form.html'
    formats=(cloudberry_import_export.JSON_FORMAT,)
    resource_class = cloudberry_app.importexport.BackendResource
    model = Backend
    form = BackendForm

    fieldsets = (
        (None, {
            'classes': ('model-info',),
            'fields': ['created',
                       'modified']
        }),
        (None, {
            'fields': ['name',
                       'group',
                       'backend',
                       'schema',
                       'transform',
                       'preview_config']
        })
    )

    
    def preview(self, request, object_id=None):        
        if object_id is None:
            obj = None
        else:
            obj = self.get_object(request, django.contrib.admin.utils.unquote(object_id), None)
            if obj is None:
                return self._get_obj_does_not_exist_redirect(request, self.model._meta, object_id)
        form = self.get_form(request, obj)(request.POST, request.FILES, instance=obj)

        if not form['preview_config'].value():
            django.contrib.messages.add_message(
                request,
                django.contrib.messages.WARNING,
                _('Please select a config to use to preview the transform'))
            return
        
        device = cloudberry_app.models.Device.objects.get(id=form['preview_config'].value())
        config = device.referred_in_configs.get(backend=form.instance.get_url(Config.schema_prefix))

        obj.transform = json.loads(form['transform'].value())
        obj.config = config.config
        obj.context = device.get_context()

        try:
            backend = obj.get_backend_instance()
        except Exception as e:
            django.contrib.messages.add_message(
                request,
                django.contrib.messages.WARNING,
                e)
            return
        
        try:
            backend.validate()
        except Exception as e:
            django.contrib.messages.add_message(
                request,
                django.contrib.messages.WARNING,
                e)

        django.contrib.messages.add_message(
            request,
            django.contrib.messages.INFO,
            django.utils.safestring.mark_safe('<div>Transformed config:</div><pre>%s</pre>' % django.utils.html.escape(json.dumps(backend.config, indent=2))))
        
    @django.contrib.admin.options.csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.method == 'POST' and '_go_preview_config' in request.POST:
            self.preview(request, object_id)
        return BaseAdmin.changeform_view(self, request, object_id, form_url, extra_context)
    
    
admin.site.register(Config, ConfigAdmin)
admin.site.register(Backend, BackendAdmin)
admin.site.register(Device, DeviceAdmin)
