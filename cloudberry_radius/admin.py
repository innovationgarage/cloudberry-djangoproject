from django.contrib import admin

from django_freeradius.base.admin import (
    AbstractNasAdmin, AbstractRadiusAccountingAdmin, AbstractRadiusCheckAdmin, AbstractRadiusGroupAdmin,
    AbstractRadiusGroupCheckAdmin, AbstractRadiusGroupReplyAdmin, AbstractRadiusGroupUsersAdmin,
    AbstractRadiusPostAuthAdmin, AbstractRadiusReplyAdmin, AbstractRadiusUserGroupAdmin,
)
from cloudberry_radius.models import (
    Nas, RadiusAccounting, Pricing, RadiusCheck, RadiusGroup, RadiusGroupCheck, RadiusGroupReply, RadiusGroupUsers,
    RadiusPostAuth, RadiusReply, RadiusUserGroup,
)


@admin.register(RadiusGroup)
class RadiusGroupAdmin(AbstractRadiusGroupAdmin):
    pass


@admin.register(RadiusGroupUsers)
class RadiusGroupUsersAdmin(AbstractRadiusGroupUsersAdmin):
    pass


@admin.register(RadiusCheck)
class RadiusCheckAdmin(AbstractRadiusCheckAdmin):
    pass


@admin.register(RadiusReply)
class RadiusReplyAdmin(AbstractRadiusReplyAdmin):
    pass


@admin.register(RadiusAccounting)
class RadiusAccountingAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'amount', 'duration', 'input_octets', 'output_octets', 'framed_ip_address', 'device_id', 'device_group_name')
    list_display_links = list_display
    search_fields = ('username', 'device_id')
    list_filter = ('start_time', 'stop_time')    

@admin.register(Pricing)
class AuthorAdmin(admin.ModelAdmin):
    readonly_fields=('latest',)
    list_display = ('latest', 'timestamp', 'group', 'cost_per_byte')
    list_display_links = list_display

@admin.register(Nas)
class NasAdmin(AbstractNasAdmin):
    pass


@admin.register(RadiusUserGroup)
class RadiusUserGroupAdmin(AbstractRadiusUserGroupAdmin):
    pass


@admin.register(RadiusGroupReply)
class RadiusGroupReplyAdmin(AbstractRadiusGroupReplyAdmin):
    pass


@admin.register(RadiusGroupCheck)
class RadiusGroupCheckAdmin(AbstractRadiusGroupCheckAdmin):
    pass


@admin.register(RadiusPostAuth)
class RadiusPostAuthAdmin(AbstractRadiusPostAuthAdmin):
    pass
