from django.db import models
from swapper import swappable_setting
from django.utils.translation import ugettext_lazy as _

from django_freeradius.base.models import (
    AbstractNas, AbstractRadiusAccounting, AbstractRadiusCheck, AbstractRadiusGroup,
    AbstractRadiusGroupCheck, AbstractRadiusGroupReply, AbstractRadiusGroupUsers, AbstractRadiusPostAuth,
    AbstractRadiusReply, AbstractRadiusUserGroup,
)


class RadiusGroup(AbstractRadiusGroup):
    pass

class RadiusGroupUsers(AbstractRadiusGroupUsers):
    pass

class RadiusCheck(AbstractRadiusCheck):
    pass

class RadiusAccounting(AbstractRadiusAccounting):
    start_delay = models.IntegerField(verbose_name=_('Start delay'),
                                      db_column='AcctStartDelay',
                                      null=True,
                                      blank=True)
    stop_delay = models.IntegerField(verbose_name=_('Stop delay'),
                                     db_column='AcctStopDelay',
                                     null=True,
                                     blank=True)
    x_ascend_session_svr_key = models.CharField(verbose_name=_('realm'),
                                                db_column='XAscendSessionSvrKey',
                                                max_length=10,
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
