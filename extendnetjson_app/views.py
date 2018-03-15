from django.views.decorators.http import last_modified
from django_netjsonconfig.views import *
import django_netjsonconfig.views

@last_modified(lambda request: start_time)
def schema(request):
    return django_netjsonconfig.views.schema(request)
