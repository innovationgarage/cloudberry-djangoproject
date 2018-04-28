import django.db.models

class DynamicTextListField(django.db.models.CharField):
    @property
    def choices(self):
        return self.choices_fn()
    @choices.setter
    def choices(self, value):
        pass
    def choices_fn(self):
        return []
