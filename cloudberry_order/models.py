from django.db import models
import django.contrib.auth.models

# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(django.contrib.auth.models.User, on_delete='cascade')
    quantity = models.IntegerField(default=1000000)
