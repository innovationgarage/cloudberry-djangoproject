from django.views.decorators.http import last_modified
from django_netjsonconfig.views import *
import django_netjsonconfig.views
import json
import cloudberry_app.models

def schema(request):
    authenticated = request.user.is_authenticated
    if callable(authenticated):
        authenticated = authenticated()
    if authenticated:
        schemas = dict(available_schemas)
        for backend in cloudberry_app.models.Backend.objects.all():
            schemas["dynamic://%s" % backend.id] = backend.schema
        c = json.dumps(schemas)
        status = 200
    else:
        c = login_required_error
        status = 403
    return HttpResponse(c, status=status, content_type='application/json')
