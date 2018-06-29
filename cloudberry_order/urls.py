from django.conf.urls import include, url, re_path

import cloudberry_order.views
from paypal.standard.pdt import views

app_name = 'cloudberry_orders'
urlpatterns = [
    url(r'^$', views.pdt, name="paypal-pdt"),
]

