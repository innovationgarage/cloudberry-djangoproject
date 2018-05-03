from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.widgets import AdminTextareaWidget
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class JsonSchemaWidget(AdminTextareaWidget):
    """
    JSON Schema Editor widget
    """
    @property
    def media(self):
        js = [#static('django-netjsonconfig/js/lib/advanced-mode.js'),
              #static('django-netjsonconfig/js/lib/tomorrow_night_bright.js'),
              static('cloudberry_app/js/libs/jsoneditor.js'),
              static('cloudberry_app/js/widget.js')]
        css = {'all': [#static('django-netjsonconfig/css/lib/jsonschema-ui.css'),
                       #static('django-netjsonconfig/css/lib/advanced-mode.css'),
                       static('cloudberry_app/css/font-awesome/css/font-awesome.min.css'),
                       static('cloudberry_app/css/json-editor.css'),
                       static('cloudberry_app/css/bootstrap-combined.min.css')]}
        return forms.Media(js=js, css=css)

    def render(self, name, value, attrs={}):
        attrs['class'] = 'vLargeTextField jsoneditor-raw'
        return super(JsonSchemaWidget, self).render(name, value, attrs)
