from django.contrib import admin

from django_freeradius.base.admin import AbstractNasAdmin
from cloudberry_radius.models import Nas

admin.site.unregister(Nas)

@admin.register(Nas)
class NasAdmin(AbstractNasAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'name', 'short_name',
                'group',
                ('type', 'custom_type'),
                'ports', 'secret', 'server', 'community', 'description'
            )
        }),
    )
