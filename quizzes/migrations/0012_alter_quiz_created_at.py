# Generated by Django 4.2.19 on 2025-02-21 03:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0011_alter_quiz_options_alter_quiz_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 21, 9, 31, 18, 132812)),
        ),
    ]
