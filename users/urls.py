from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = [
#    path('signup/', views.SignUp.as_view(), name='signup'),
    url(r'^$', views.home, name='home'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate'),
]
