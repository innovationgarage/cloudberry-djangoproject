from django.db import models
import django.contrib.auth.models

# Create your models here.

class Order(models.Model):
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    user = models.ForeignKey(django.contrib.auth.models.User,
                             on_delete='cascade',
                             related_name='orders')
    quantity = models.IntegerField(default=1000000)
