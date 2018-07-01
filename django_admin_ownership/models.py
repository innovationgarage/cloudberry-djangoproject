# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import django.contrib.auth.models

try:
    import django_global_request.middleware
    def get_current_user():
        request = django_global_request.middleware.get_request()
        return request and request.user
except:
    def get_current_user():
        return None
    
class GroupedConfigurationMixin(object):
    def get_default_group(self, user):
        user = user or get_current_user()
        is_superuser = user and user.is_superuser
        groups = ConfigurationGroup.objects.all()
        if is_superuser:
            groups = groups.filter(group = None)
        else:
            groups = groups.filter(write__user = user)
        if len(groups):
            return groups[0]
        return None

    def save(self, *arg, **kw):
        field_name = self._configuration_group[0]        
        is_none = getattr(self, field_name, None) is None
        blank = getattr(type(self), field_name).field.blank
        user = get_current_user()
        is_superuser = user and user.is_superuser
        if is_none and (not blank
                        or not is_superuser):
            setattr(self, field_name, self.get_default_group(user))
        super().save(*arg, **kw)

class ConfigurationGroup(models.Model):
    _configuration_group = ['group']
    
    name = models.CharField(max_length=64,
                            unique=True,
                            db_index=True)
    owner = models.ForeignKey('auth.User', blank=True, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey('ConfigurationGroup', blank=True, null=True, on_delete=models.CASCADE)
    read = models.ManyToManyField('auth.Group', related_name="read_devices", blank=True)
    write = models.ManyToManyField('auth.Group', related_name="write_devices", blank=True)

    class Meta:
        verbose_name = 'Configuration group'
        app_label = 'auth'
        
    def __str__(self):
        return self.name

django.contrib.auth.models.Group.add_to_class(
    'group', models.ForeignKey(ConfigurationGroup,
                               blank=True,
                               null=True,
                               on_delete=models.CASCADE, related_name='group_for_user_group'))
django.contrib.auth.models.Group._configuration_group = ["group"]
