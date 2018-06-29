from django.conf.urls import include, url, re_path

import cloudberry_order.views

#  API is broken, disable for now
app_name = 'freeradius'
urlpatterns = [
    re_path(r'^cloudberry_order/account-balance', cloudberry_order.views.account_balance, name='account_balance'),
]
