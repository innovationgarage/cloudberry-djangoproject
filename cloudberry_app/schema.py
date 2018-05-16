import django.apps
import django_global_request.middleware

def add_foreign_key(schema, model, title):
    app_label, cls = model.rsplit(".", 1)
    model_cls = django.apps.apps.get_registered_model(app_label, cls)
    instances = model_cls.objects.all()
    if hasattr(model_cls, "objects_allowed_to"):
        instances = model_cls.objects_allowed_to(
            instances,
            read=django_global_request.middleware.get_request().user
        )
    instances = instances.order_by(title)
    titles = [getattr(instance, title) for instance in instances]
    values = ["fk://%s/%s" % (model, instance.id)
              for instance in instances]
    if values:
        schema['definitions']['fk__%s' % model.replace(".", "__")] = {
            'title': cls,
            'type': 'string',
            'options': {'enum_titles': titles},
            'enum': values,
            'fk_model': model,
            'add_url': '/admin/%s/%s/add/?_to_field=id&_popup=1' % (app_label, model_cls._meta.model_name),
            'change_url': '/admin/%s/%s/__fk__/change/?_to_field=id&amp;_popup=1' % (app_label, model_cls._meta.model_name)
        }
    else:
        schema['definitions']['fk__%s' % model.replace(".", "__")] = {
            'title': cls,
            'type': 'object'
        }

def find_foreign_keys(schema):
    # Finds {"$ref": "#/definitions/fk__cloudberry_app__Device"} schema items and yields
    # ("cloudberry_app.Device", {"$ref": "#/definitions/fk__cloudberry_app__Device"})
    if not hasattr(schema, 'items'): return
    if "$ref" in schema and schema["$ref"].startswith("#/definitions/fk__"):
        yield (schema["$ref"].split("#/definitions/fk__")[1].replace("__", "."), schema)
    for name, value in schema.items():
        if name == "$ref": continue
        for fk in find_foreign_keys(value):
            yield fk

def schema_add_foreign_keys(schema):
    schema = dict(schema)
    if 'definitions' not in schema:
        schema['definitions'] = {}
    for model, data in list(find_foreign_keys(schema)):
        add_foreign_key(schema, model, data.get("title", "name"))
    return schema

def schema_add_device(schema):
    if 'cloudberry_app.Device' not in (model for (model, data) in find_foreign_keys(schema)):
        schema['properties']['device'] = {
            "type": "object",
            "properties": {
                "device": {"$ref": "#/definitions/fk__cloudberry_app__Device", "title": "name"}
            }
        }
        if 'required' not in schema:
            schema['required'] = []
        schema['required'].append('Device')
    return schema

def extend_schema(schema):
    return schema_add_foreign_keys(
        schema_add_device(schema))
