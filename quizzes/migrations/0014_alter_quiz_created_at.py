# Generated by Django 4.2.19 on 2025-02-21 04:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0013_userprofile_created_at_alter_quiz_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 21, 10, 4, 4, 706054)),
        ),
    ]
