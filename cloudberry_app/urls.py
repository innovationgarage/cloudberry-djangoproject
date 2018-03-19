from django.conf.urls import url, re_path

from . import views

app_name = 'cloudberry_app'

urlpatterns = [
    url(r'^netjsonconfig/schema\.json$', views.schemas, name='schema'),
    re_path(r'^cloudberry_app/schema/backend/(?P<schema>.*)$', views.schema_backend, name='backend_schema'),
    re_path(r'^cloudberry_app/schema/dynamic/(?P<schema>.*)$', views.schema_dynamic, name='dynamic_schema'),
    re_path(r'^cloudberry_app/schema/meta$', views.schema_meta, name='meta_schema'),
]
