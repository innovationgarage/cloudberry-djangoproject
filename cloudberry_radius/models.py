from django.db import models
from swapper import swappable_setting

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
    pass

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
