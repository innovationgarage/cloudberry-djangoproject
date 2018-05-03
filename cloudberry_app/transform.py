import django.db.models
import django.apps

def model_to_dict(model):
    def mangle(value):
        if isinstance(value, (bool, type(None), str, int, float)):
            return value
        elif isinstance(value, django.db.models.Model):
            return "fk://%s/%s" % (value._meta.label, value.id)
        elif hasattr(value, 'items'):
            return type(value)({item_name: mangle(item_value)
                                for item_name, item_value in value.items()})
        elif hasattr(value, '__iter__'):
            return type(value)(mangle(item_value)
                               for item_value in value)
        else:
            return str(value)
    res = {f.name: mangle(getattr(model, f.name))
           for f in model._meta.fields}
    res['pk'] = "fk://%s/%s" % (model._meta.label, model.id)
    return res

class FkLookup(object):
    def __getitem__(self, name):
        if "://" in name:
            name = name.split("://")[1]
        if '/' in name:
            name, id = name.split("/")
            return FkLookupModel(name)[id]
        else:
            return FkLookupModel(name)
        
    def __contains__(self, name):
        if "://" in name:
            name = name.split("://")[1]
        if '/' in name:
            name, id = name.split("/")
            return id in FkLookupModel(name)
        else:
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
