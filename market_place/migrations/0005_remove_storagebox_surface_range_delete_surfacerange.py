# Generated by Django 4.2.5 on 2023-11-01 20:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market_place', '0004_surfacerange_storagebox_surface_range'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storagebox',
            name='surface_range',
        ),
        migrations.DeleteModel(
            name='SurfaceRange',
        ),
    ]