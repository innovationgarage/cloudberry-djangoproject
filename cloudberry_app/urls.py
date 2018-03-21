from django.conf.urls import url, re_path

from . import views

app_name = 'cloudberry_app'

urlpatterns = [
    re_path(r'^cloudberry_app/schema/backend/(?P<schema>.*)$', views.schema_backend, name='backend_schema'),
    re_path(r'^cloudberry_app/schema/dynamic/(?P<schema>.*)$', views.schema_dynamic, name='dynamic_schema'),
    re_path(r'^cloudberry_app/schema/meta$', views.schema_meta, name='meta_schema'),

    re_path(r'^cloudberry_app/schema/transform/backend/(?P<schema>.*)$', views.schema_transform_backend, name='transform_backend_schema'),
    re_path(r'^cloudberry_app/schema/transform/dynamic/(?P<schema>.*)$', views.schema_transform_dynamic, name='transform_dynamic_schema'),
]
