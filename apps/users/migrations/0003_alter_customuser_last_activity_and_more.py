# Generated by Django 4.1.7 on 2023-03-05 11:43

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_customuser_last_activity_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="last_activity",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="last_login_time",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]