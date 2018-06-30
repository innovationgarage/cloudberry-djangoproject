from django.views.decorators.http import last_modified
from django_netjsonconfig.views import *
import django_netjsonconfig.views
import json
import cloudberry_app.models
import cloudberry_app.schema
import os.path
import traceback
from django.conf import settings
import urllib.parse

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
        c = cloudberry_app.schema.extend_schema(
            available_schemas[schema])
        status = 200
    return HttpResponse(json.dumps(c), status=status, content_type='application/json')


@check_auth
def schema_dynamic(request, schema):
    try:
        c = cloudberry_app.models.Backend.objects.get(id=schema).extended_schema
        status = 200
    except Exception as e:
        print(e)
        traceback.print_exc()
        c = {"error": "Not found"}
        status = 404
    return HttpResponse(json.dumps(c), status=status, content_type='application/json')

@check_auth
def schema_meta(request):
    return HttpResponse(json.dumps(meta_schema), status=200, content_type='application/json')

@check_auth
def download_device_image(request, device):
    device = cloudberry_app.models.Device.objects.get(pk=device)

    url = "%s/%s?OPENWISP_UUID=%s&OPENWISP_KEY=%s&OPENWISP_URL=%s&SERVER=%s" % (
        settings.OPENWISP_DEVICE_IMAGE_URL,
        device.os_image,
        device.pk,
        device.key,
        urllib.parse.quote(request.build_absolute_uri(settings.ROOT)),
        request.META["SERVER_NAME"]
    )

    with urllib.request.urlopen(url) as f:
        status = f.getcode()
        try:
            res = json.load(f)
        except Exception as e:
            res = {"error": str(e)}

    if status != 200 or 'output_file' not in res:
        res["url"] = url
        return HttpResponse(json.dumps(res), status=500, content_type='text/json')

    image_path = os.path.join(settings.OPENWISP_DEVICE_IMAGES, res["output_file"])
    with open(image_path, 'rb') as f:
        resp = HttpResponse(f.read(), status=200, content_type='application/binary')
        resp['Content-Disposition'] = 'attachment; filename="%s.img"' % device.pk

        return resp
