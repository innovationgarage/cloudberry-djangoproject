# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class ConfigurationGroup(models.Model):
    name = models.CharField(max_length=64,
                            unique=True,
                            db_index=True)
    read = models.ManyToManyField('auth.Group', related_name="read_devices", blank=True)
    write = models.ManyToManyField('auth.Group', related_name="write_devices", blank=True)

    class Meta:
        verbose_name = 'Configuration group'
        app_label = 'auth'
        
    def __str__(self):
        return self.name

    __configuration_group = []
