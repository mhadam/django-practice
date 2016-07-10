# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0005_userprofile_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='first_visit',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 10, 18, 27, 34, 793341), null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='last_visit',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 10, 18, 27, 34, 793302), null=True),
            preserve_default=True,
        ),
    ]
