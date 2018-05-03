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
        html = """
<input class="button json-editor-btn-edit advanced-mode" type="button" value="{0}">
<label id="netjsonconfig-hint">
    Want learn to use the advanced mode? Consult the
    <a href="http://netjsonconfig.openwisp.org/en/stable/general/basics.html"
       target="_blank">netjsonconfig documentation</a>.
</label>
"""
        html = html.format(_('Advanced mode (raw JSON)'),)
        html += super(JsonSchemaWidget, self).render(name, value, attrs)
        return html
