from django.db import models
from swapper import swappable_setting
from django.utils.translation import ugettext_lazy as _

from django_freeradius.base.models import (
    AbstractNas, AbstractRadiusAccounting, AbstractRadiusCheck, AbstractRadiusGroup,
    AbstractRadiusGroupCheck, AbstractRadiusGroupReply, AbstractRadiusGroupUsers, AbstractRadiusPostAuth,
    AbstractRadiusReply, AbstractRadiusUserGroup,
)

import django_admin_ownership.models
import cloudberry_app.models
import django.contrib.auth.models
import datetime
import uuid

class RadiusGroup(AbstractRadiusGroup):
    pass

class RadiusGroupUsers(AbstractRadiusGroupUsers):
    pass

class RadiusCheck(AbstractRadiusCheck):
    pass

class RadiusAccounting(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='radacctid')
    session_id = models.CharField(verbose_name=_('session ID'),
                                  max_length=64,
                                  db_column='acctsessionid',
                                  db_index=True,
                                  null=True,
                                  blank=True)
    unique_id = models.CharField(verbose_name=_('accounting unique ID'),
                                 max_length=32,
                                 db_column='acctuniqueid',
                                 unique=True,
                                 null=True,
                                 blank=True)
    groupname = models.CharField(verbose_name=_('group name'),
                                 max_length=64,
                                 null=True,
                                 blank=True)
    realm = models.CharField(verbose_name=_('realm'),
                             max_length=64,
                             null=True,
                             blank=True)
    nas_ip_address = models.GenericIPAddressField(verbose_name=_('NAS IP address'),
                                                  db_column='nasipaddress',
                                                  db_index=True,
                                                  null=True,
                                                  blank=True)
    nas_port_id = models.CharField(verbose_name=_('NAS port ID'),
                                   max_length=15,
                                   db_column='nasportid',
                                   null=True,
                                   blank=True)
    nas_port_type = models.CharField(verbose_name=_('NAS port type'),
                                     max_length=32,
                                     db_column='nasporttype',
                                     null=True,
                                     blank=True)
    start_time = models.DateTimeField(verbose_name=_('start time'),
                                      db_column='acctstarttime',
                                      db_index=True,
                                      null=True,
                                      blank=True)
    update_time = models.DateTimeField(verbose_name=_('update time'),
                                       db_column='acctupdatetime',
                                       null=True,
                                       blank=True)
    stop_time = models.DateTimeField(verbose_name=_('stop time'),
                                     db_column='acctstoptime',
                                     db_index=True,
                                     null=True,
                                     blank=True)
    interval = models.IntegerField(verbose_name=_('interval'),
                                   db_column='acctinterval',
                                   null=True,
                                   blank=True)
    session_time = models.PositiveIntegerField(verbose_name=_('session time'),
                                               db_column='acctsessiontime',
                                               null=True,
                                               blank=True)
    authentication = models.CharField(verbose_name=_('authentication'),
                                      max_length=32,
                                      db_column='acctauthentic',
                                      null=True,
                                      blank=True)
    connection_info_start = models.CharField(verbose_name=_('connection info start'),
                                             max_length=50,
                                             db_column='connectinfo_start',
                                             null=True,
                                             blank=True)
    connection_info_stop = models.CharField(verbose_name=_('connection info stop'),
                                            max_length=50,
                                            db_column='connectinfo_stop',
                                            null=True,
                                            blank=True)
    input_octets = models.BigIntegerField(verbose_name=_('input octets'),
                                          db_column='acctinputoctets',
                                          null=True,
                                          blank=True)
    output_octets = models.BigIntegerField(verbose_name=_('output octets'),
                                           db_column='acctoutputoctets',
                                           null=True,
                                           blank=True)
    called_station_id = models.CharField(verbose_name=_('called station ID'),
                                         max_length=50,
                                         db_column='calledstationid',
                                         blank=True,
                                         null=True)
    calling_station_id = models.CharField(verbose_name=_('calling station ID'),
                                          max_length=50,
                                          db_column='callingstationid',
                                          blank=True,
                                          null=True)
    terminate_cause = models.CharField(verbose_name=_('termination cause'),
                                       max_length=32,
                                       db_column='acctterminatecause',
                                       blank=True,
                                       null=True)
    service_type = models.CharField(verbose_name=_('service type'),
                                    max_length=32,
                                    db_column='servicetype',
                                    null=True,
                                    blank=True)
    framed_protocol = models.CharField(verbose_name=_('framed protocol'),
                                       max_length=32,
                                       db_column='framedprotocol',
                                       null=True,
                                       blank=True)
    framed_ip_address = models.GenericIPAddressField(verbose_name=_('framed IP address'),
                                                     db_column='framedipaddress',
                                                     db_index=True,
                                                     # the default MySQL freeradius schema defines
                                                     # this as NOT NULL but defaulting to empty string
                                                     # but that wouldn't work on PostgreSQL
                                                     null=True,
                                                     blank=True)    
    user = models.ForeignKey(django.contrib.auth.models.User,
                             to_field="username",
                             db_column="username",
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True,
                             related_name='radius_accounting')
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
                               blank=True,
                               related_name='radius_accounting')
    amount = models.FloatField(verbose_name=_('Amount'),
                               db_column='amount',
                               null=True,
                               blank=True)

    @property
    def duration(self):
        if self.stop_time is None or self.start_time is None: return None
        return self.stop_time - self.start_time
    
    @property
    def device_group_name(self):
        if self.device is None: return None
        return self.device.group.name
    
    @property
    def group_name(self):
        return self.group.name

    @property
    def username(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.unique_id is None:
            self.unique_id = uuid.uuid4().hex
        if not self.start_time:
            self.start_time = datetime.datetime.now()
        super(RadiusAccounting, self).save(*args, **kwargs)

    class Meta:
        db_table = 'radacct'
        verbose_name = _('accounting')
        verbose_name_plural = _('accountings')

    def __str__(self):
        return self.unique_id


class Pricing(models.Model):
    class Meta:
        db_table = 'radprice'

    timestamp = models.DateTimeField(verbose_name=_('Time'),
                                     auto_now_add=True,
                                     db_column='timestamp')
    latest = models.BooleanField(blank=True)
    group = models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                              on_delete=models.CASCADE,
                              related_name='radius_pricing')
    cost_per_byte = models.FloatField(verbose_name=_('Cost per byte'),
                                      db_column='cost',
                                      null=True,
                                      blank=True)

    def save(self):
        if self.latest is None:
            for existing in self.group.radius_pricing.filter(latest=True):
                existing.latest = False
                existing.save()
            self.latest = True
        super(Pricing, self).save()
    
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
