# Generated by Django 2.0.6 on 2018-06-29 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloudberry_radius', '0009_auto_20180629_1454'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='radiusaccounting',
            name='cost',
        ),
        migrations.AddField(
            model_name='radiusaccounting',
            name='amount',
            field=models.FloatField(blank=True, db_column='amount', null=True, verbose_name='Amount'),
        ),
    ]
