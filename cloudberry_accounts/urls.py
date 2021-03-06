from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
import cloudberry_accounts.views
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^$', cloudberry_accounts.views.homepage, name='index'),
    url(r'^admin/login/?', RedirectView.as_view(pattern_name='login')),
    url(r'^accounts/register/$', cloudberry_accounts.views.register, name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/profile/', TemplateView.as_view(template_name='cloudberry_accounts/profile.html'), name='profile'),
    url(r'^login/', auth_views.login, name='login'),
]
