# Generated by Django 2.0.6 on 2018-06-26 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloudberry_radius', '0002_auto_20180626_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='radiusaccounting',
            name='x_ascend_session_svr_key',
            field=models.CharField(blank=True, db_column='XAscendSessionSvrKey', max_length=10, null=True, verbose_name='realm'),
        ),
    ]
