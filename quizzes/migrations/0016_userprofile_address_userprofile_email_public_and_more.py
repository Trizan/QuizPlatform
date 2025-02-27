# Generated by Django 4.2.19 on 2025-02-21 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0015_quiz_liked_by_alter_quiz_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='show_address',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='show_phone_number',
            field=models.BooleanField(default=False),
        ),
    ]
