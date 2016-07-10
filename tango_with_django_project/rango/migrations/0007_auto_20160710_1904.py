# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0006_auto_20160710_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='first_visit',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='last_visit',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
    ]
