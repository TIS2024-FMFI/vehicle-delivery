# Generated by Django 5.1.4 on 2025-01-21 09:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_rename_registration_number_transportmodel_registration_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='communicationmodel',
            name='date',
            field=models.DateField(blank=True, default=datetime.date.today, null=True),
        ),
    ]
