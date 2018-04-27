# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DjangoAdminOwnershipConfig(AppConfig):
    name = 'django_admin_ownership'
    
    def ready(self):
        import django_admin_ownership.row_access
        django_admin_ownership.row_access.add_row_access_to_all()

