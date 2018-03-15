from django.conf.urls import url

from . import views

app_name = 'cloudberry_app'

urlpatterns = [
    url(r'^netjsonconfig/schema\.json$', views.schema, name='schema'),
]
