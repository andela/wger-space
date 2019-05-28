# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2019-05-29 08:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='log',
            options={'ordering': ['-date']},
        ),
        migrations.AlterField(
            model_name='log',
            name='gym',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='email_log', to='gym.Gym'),
        ),
    ]
