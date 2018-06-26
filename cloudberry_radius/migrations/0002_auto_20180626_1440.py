# Generated by Django 2.0.6 on 2018-06-26 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloudberry_radius', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='radiusaccounting',
            name='start_delay',
            field=models.IntegerField(blank=True, db_column='AcctStartDelay', null=True, verbose_name='Start delay'),
        ),
        migrations.AddField(
            model_name='radiusaccounting',
            name='stop_delay',
            field=models.IntegerField(blank=True, db_column='AcctStopDelay', null=True, verbose_name='Stop delay'),
        ),
    ]
