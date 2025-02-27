from django.db.models.signals import post_migrate
from django.contrib.auth.models import User
from django.dispatch import receiver

@receiver(post_migrate)
def ensure_system_user_exists(sender, **kwargs):
    if not User.objects.filter(username="System").exists():
        User.objects.create_user(username="System", password="Nepal@123", avatar="default_avatars\system.jpg")
