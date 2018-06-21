"""cloudberry_djangoproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='cloudberry_accounts/index.html'), name='index'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/profile/', TemplateView.as_view(template_name='cloudberry_accounts/profile.html'), name='profile'),
    url(r'^login/', auth_views.login, name='login'),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^', include('cloudberry_app.controller.urls', namespace='controller')),
    url(r'^', include('cloudberry_app.urls', namespace='netjsonconfig')),
    url(r'^', include('django_x509.urls', namespace='x509')),
    url(r'^', include('django_freeradius.urls', namespace='freeradius')),

]

# extendnetjson: django_netjsonconfig requires staticfiles to
# function, as the admin interface uses custom javascript for the
# schema-based json editor.
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
