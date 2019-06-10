# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2019-06-10 15:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20160303_2340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='license',
            name='full_name',
            field=models.CharField(help_text='If a license has been localized, e.g. the Creative Commons licenses for the different countries, add them as separate entries here.', max_length=60, verbose_name='Full name'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='show_english_ingredients',
            field=models.BooleanField(default=True, help_text='Check to also show ingredients in English while creating\na nutritional plan. These ingredients are extracted from a list provided\nby the US Department of Agriculture. It is extremely complete, with around\n7000 entries, but can be somewhat overwhelming and make the search difficult.\n', verbose_name='Also use ingredients in English'),
        ),
    ]
