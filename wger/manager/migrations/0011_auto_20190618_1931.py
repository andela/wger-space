# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2019-06-18 16:31
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0010_auto_20190618_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='reps',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(600)], verbose_name='Amount'),
        ),
    ]
