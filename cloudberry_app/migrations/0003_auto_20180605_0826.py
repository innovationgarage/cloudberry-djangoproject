# Generated by Django 2.0.5 on 2018-06-05 08:26

import cloudberry_app.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloudberry_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='os_image',
            field=cloudberry_app.fields.DynamicTextListField(blank=True, help_text='Select OS image', max_length=128, verbose_name='os image'),
        ),
        migrations.AlterField(
            model_name='device',
            name='backend',
            field=models.CharField(blank=True, choices=[('/cloudberry_app/schema/backend/cloudberry_netjson.OpenWrt', 'OpenWRT/Cloudberry'), ('/cloudberry_app/schema/backend/netjsonconfig.OpenWrt', 'OpenWRT/LEDE'), ('/cloudberry_app/schema/backend/netjsonconfig.OpenWisp', 'OpenWISP Firmware 1.x')], help_text='Select <a href="http://netjsonconfig.openwisp.org/en/stable/" target="_blank">netjsonconfig</a> backend', max_length=128, verbose_name='backend'),
        ),
    ]
