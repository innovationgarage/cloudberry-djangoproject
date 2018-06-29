from django.db import models
from swapper import swappable_setting
from django.utils.translation import ugettext_lazy as _

from django_freeradius.base.models import (
    AbstractNas, AbstractRadiusAccounting, AbstractRadiusCheck, AbstractRadiusGroup,
    AbstractRadiusGroupCheck, AbstractRadiusGroupReply, AbstractRadiusGroupUsers, AbstractRadiusPostAuth,
    AbstractRadiusReply, AbstractRadiusUserGroup,
)

import cloudberry_app.models
import django.contrib.auth.models

class RadiusGroup(AbstractRadiusGroup):
    pass

class RadiusGroupUsers(AbstractRadiusGroupUsers):
    pass

class RadiusCheck(AbstractRadiusCheck):
    pass

class RadiusAccounting(AbstractRadiusAccounting):
    @property
    def username(self):
        return self.user.username
    
    user = models.ForeignKey(django.contrib.auth.models.User,
                             to_field="username",
                             db_column="username",
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)
    
    start_delay = models.IntegerField(verbose_name=_('Start delay'),
                                      db_column='acctstartdelay',
                                      null=True,
                                      blank=True)
    stop_delay = models.IntegerField(verbose_name=_('Stop delay'),
                                     db_column='acctstopdelay',
                                     null=True,
                                     blank=True)
    x_ascend_session_svr_key = models.CharField(verbose_name=_('realm'),
                                                db_column='xascendsessionsvrkey',
                                                max_length=10,
                                                null=True,
                                                blank=True)
    
    device = models.ForeignKey(cloudberry_app.models.Device,
                               db_column='nasidentifier',
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True)

class RadiusReply(AbstractRadiusReply):
    pass

class Nas(AbstractNas):
    pass

class RadiusGroupCheck(AbstractRadiusGroupCheck):
    pass

class RadiusGroupReply(AbstractRadiusGroupReply):
    pass

class RadiusPostAuth(AbstractRadiusPostAuth):
    pass

class RadiusUserGroup(AbstractRadiusUserGroup):
    pass
