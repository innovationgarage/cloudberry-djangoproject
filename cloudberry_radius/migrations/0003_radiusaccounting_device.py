# Generated by Django 2.0.6 on 2018-06-29 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cloudberry_app', '0005_remove_device_generated_image_id'),
        ('cloudberry_radius', '0002_auto_20180626_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='radiusaccounting',
            name='device',
            field=models.ForeignKey(blank=True, db_column='nasidentifier', null=True, on_delete=django.db.models.deletion.CASCADE, to='cloudberry_app.Device'),
        ),
    ]
