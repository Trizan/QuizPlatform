# Generated by Django 4.2.19 on 2025-02-22 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0018_notification_notification_type_quiz_is_deleted_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='notification_type',
        ),
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('info', 'Information'), ('warning', 'Warning'), ('achievement', 'Achievement')], default='info', max_length=20),
        ),
        migrations.AddField(
            model_name='quiz',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
