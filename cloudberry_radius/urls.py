from django.conf.urls import include, url, re_path

import cloudberry_radius.views

#  API is broken, disable for now
app_name = 'cloudberry_radius'
urlpatterns = [
    re_path(r'^cloudberry_radius/account_balance', cloudberry_radius.views.account_balance, name='account_balance'),
    re_path(r'^admin/cloudberry_radius/account_balance/?$', cloudberry_radius.views.device_owner_account_balance, name='device_owner_account_balance'),
    url(r'^cloudberry_radius/payment$', cloudberry_radius.views.pdt, name="payment_done"),
]
