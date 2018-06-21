# Generated by Django 2.0.6 on 2018-06-21 07:47

import cloudberry_app.backends
import cloudberry_app.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_admin_ownership.models
import django_netjsonconfig.utils
import jsonfield.fields
import model_utils.fields
import re
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0010_configurationgroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='Backend',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(db_index=True, max_length=64, unique=True)),
                ('backend', cloudberry_app.fields.DynamicTextListField(blank=True, help_text='Select <a href="http://netjsonconfig.openwisp.org/en/stable/" target="_blank">netjsonconfig</a> backend', max_length=128, verbose_name='backend')),
                ('schema', jsonfield.fields.JSONField(blank=True, default=dict, help_text='<a target="_blank" href="http://json-schema.org/">JSONSchema</a> for the configuration', verbose_name='schema')),
                ('transform', jsonfield.fields.JSONField(blank=True, default=dict, help_text='<a target="_blank" href="https://innovationgarage.github.io/cloudberry-djangoproject/docs/backends.html">Transform</a> of the configuration', verbose_name='transform')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.ConfigurationGroup')),
            ],
            options={
                'abstract': False,
            },
            bases=(django_admin_ownership.models.GroupedConfigurationMixin, models.Model, cloudberry_app.backends.BackendedModelMixin, cloudberry_app.backends.TemplatedBackendModelMixin),
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(db_index=True, max_length=64, unique=True)),
                ('config', jsonfield.fields.JSONField(default=dict, help_text='configuration in NetJSON DeviceConfiguration format', verbose_name='configuration')),
                ('backend', cloudberry_app.fields.DynamicTextListField(blank=True, help_text='Select <a href="http://netjsonconfig.openwisp.org/en/stable/" target="_blank">netjsonconfig</a> backend', max_length=128, verbose_name='backend')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.ConfigurationGroup')),
                ('refers_configs', models.ManyToManyField(related_name='referred_in_configs', to='cloudberry_app.Config')),
            ],
            options={
                'abstract': False,
            },
            bases=(django_admin_ownership.models.GroupedConfigurationMixin, cloudberry_app.backends.BackendedModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(db_index=True, max_length=64, unique=True)),
                ('key', models.CharField(db_index=True, default=django_netjsonconfig.utils.get_random_key, help_text='unique device key', max_length=64, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[^\\s/\\.]+$'), code='invalid', message='Key must not contain spaces, dots or slashes.')])),
                ('model', models.CharField(blank=True, db_index=True, help_text='device model and manufacturer', max_length=64)),
                ('os', models.CharField(blank=True, db_index=True, help_text='operating system identifier', max_length=128, verbose_name='operating system')),
                ('system', models.CharField(blank=True, db_index=True, help_text='system on chip or CPU info', max_length=128, verbose_name='SOC / CPU')),
                ('notes', models.TextField(blank=True)),
                ('mac_address', models.CharField(blank=True, db_index=True, help_text='primary mac address', max_length=17, null=True, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'), code='invalid', message='Must be a valid mac address.')])),
                ('status', model_utils.fields.StatusField(choices=[('modified', 'modified'), ('running', 'running'), ('error', 'error')], default='modified', help_text='modified means the configuration is not applied yet; running means applied and running; error means the configuration caused issues and it was rolledback', max_length=100, no_check_for_status=True)),
                ('last_ip', models.GenericIPAddressField(blank=True, help_text='indicates the last ip from which the configuration was downloaded from (except downloads from this page)', null=True)),
                ('backend', models.CharField(blank=True, choices=[('/cloudberry_app/schema/backend/cloudberry_netjson.OpenWrt', 'OpenWRT/Cloudberry'), ('/cloudberry_app/schema/backend/netjsonconfig.OpenWrt', 'OpenWRT/LEDE'), ('/cloudberry_app/schema/backend/netjsonconfig.OpenWisp', 'OpenWISP Firmware 1.x')], help_text='Select <a href="http://netjsonconfig.openwisp.org/en/stable/" target="_blank">netjsonconfig</a> backend', max_length=128, verbose_name='backend')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.ConfigurationGroup')),
            ],
            options={
                'abstract': False,
            },
            bases=(django_admin_ownership.models.GroupedConfigurationMixin, models.Model, cloudberry_app.backends.BackendedModelMixin),
        ),
        migrations.AddField(
            model_name='config',
            name='refers_devices',
            field=models.ManyToManyField(related_name='referred_in_configs', to='cloudberry_app.Device'),
        ),
    ]
