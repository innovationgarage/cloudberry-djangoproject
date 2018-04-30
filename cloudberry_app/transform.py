import django.db.models
import django.apps

def model_to_dict(model):
    def mangle(value):
        if isinstance(value, (bool, type(None), str, int, float)):
            return value
        elif isinstance(value, django.db.models.Model):
            return {'model': "%s.%s" % (value._meta.app_label, value._meta.model_name),
                    'id': str(value.id)}
        elif hasattr(value, 'items'):
            return type(value)({item_name: mangle(item_value)
                                for item_name, item_value in value.items()})
        elif hasattr(value, '__iter__'):
            return type(value)(mangle(item_value)
                               for item_value in value)
        else:
            return str(value)
    return {f.name: mangle(getattr(model, f.name))
            for f in model._meta.fields}    
        
class FkLookup(object):
    def __getitem__(self, name):
        return FkLookupModel(name)

    def __contains__(self, name):
        try:
            FkLookupModel(name)
            return True
        except:
            return False

    def items(self):
        return []

    def values(self):
        return []
    
    def __repr__(self):
        return 'FkLookup'
    
class FkLookupModel(object):
    def __init__(self, model):
        self.model_name = model
        try:
            self.model = django.apps.apps.get_registered_model(*model.split("."))
        except:
            raise Exception("Unable to get registered model %s" % model)

    def __contains__(self, id):
        return self.model.objects.filter(id=id).count() > 0
        
    def __getitem__(self, id):
        try:
            return model_to_dict(self.model.objects.get(id=id))
        except Exception as e:
            raise Exception("%s.objects.get(id=%s): %s" % (self.model_name, repr(id), e))

    def items(self):
        for model in self.model.objects.all():
            yield (model.id, model_to_dict(model))

    def values(self):
        for model in self.model.objects.all():
            yield model_to_dict(model)
            
    def __repr__(self):
        return self.model_name
