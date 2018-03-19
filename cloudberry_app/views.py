from django.views.decorators.http import last_modified
from django_netjsonconfig.views import *
import django_netjsonconfig.views
import json
import cloudberry_app.models
import os.path

with open(os.path.join(os.path.dirname(__file__), "json-schema-meta-schema.json")) as f:
    meta_schema = json.load(f)

def check_auth(fn):
    def wrapper(request, *arg, **kw):
        authenticated = request.user.is_authenticated
        if callable(authenticated):
            authenticated = authenticated()
        if not authenticated:
            c = login_required_error
            status = 403
            return HttpResponse(c, status=status, content_type='application/json')
        return fn(request, *arg, **kw)        
    return wrapper

@check_auth
def schema_backend(request, schema):
    c = {"error": "Not found"}
    status = 404
    if schema in available_schemas:
        c = available_schemas[schema]
        status = 200
    return HttpResponse(json.dumps(c), status=status, content_type='application/json')


@check_auth
def schema_dynamic(request, schema):
    try:
        c = cloudberry_app.models.Backend.objects.get(id=schema).schema
        status = 200
    except:
        c = {"error": "Not found"}
        status = 404
    return HttpResponse(json.dumps(c), status=status, content_type='application/json')

@check_auth
def schema_meta(request):
    return HttpResponse(json.dumps(meta_schema), status=200, content_type='application/json')
