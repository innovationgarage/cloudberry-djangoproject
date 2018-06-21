from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^process/$', views.view_that_asks_for_money, name="process"),
]
