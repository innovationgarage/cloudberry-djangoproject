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


class AccountBalance(object):
    class _meta(object):
        swapped = False
        app_config = None
        abstract = False
        model_name = 'account_balance'
        app_label = 'cloudberry_radius'
        verbose_name_plural = 'Account balance'
        verbose_name = 'Account balance'
        object_name = 'account_balance'
        
@admin.register(AccountBalance)
class AccountBalanceAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return True
    def get_model_perms(self, request):
        return {"change": True}

@admin.register(RadiusAccounting)
class RadiusAccountingAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'amount', 'duration', 'input_octets', 'output_octets', 'framed_ip_address', 'device_id', 'device_group_name')
    list_display_links = list_display
    search_fields = ('username', 'device_id')
    list_filter = ('start_time', 'stop_time')    

@admin.register(Pricing)
class PricingAdmin(admin.ModelAdmin):
    readonly_fields=('latest','timestamp')
    list_display = ('latest', 'timestamp', 'group', 'cost_per_byte')
    list_display_links = list_display
    
    add_fieldsets = ((None, {"fields": ["group", "cost_per_byte"]}),)
    change_fieldsets = ((None, {"fields": ["timestamp", "latest"]}),
                        (None, {"fields": ["group", "cost_per_byte"]}),)
    
    def add_view(self,request,extra_content=None):
         self.fieldsets = self.add_fieldsets
         return super(PricingAdmin,self).add_view(request)
    
    def change_view(self,request,object_id,extra_content=None):
         self.fieldsets = self.change_fieldsets
         return super(PricingAdmin,self).change_view(request,object_id)
    
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
