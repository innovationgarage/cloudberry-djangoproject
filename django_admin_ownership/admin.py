# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.admin
import django_admin_ownership.models

class ConfigurationGroupAdmin(django.contrib.admin.ModelAdmin):
    pass

django.contrib.admin.site.register(
    django_admin_ownership.models.ConfigurationGroup,
    ConfigurationGroupAdmin)
