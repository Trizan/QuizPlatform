print("✅ signals.py loaded!")  # Debugging print

from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model
from django.dispatch import receiver

User = get_user_model()

@receiver(post_migrate)
def ensure_system_user_exists(sender, **kwargs):
    print(f"🚀 post_migrate triggered for sender: {sender}")  # Debugging print

    if not User.objects.filter(username="System").exists():
        print("🛠️ Creating System user...")
        User.objects.create_user(username="System", password="Nepal@123")
        print("✅ System user created successfully!")
    else:
        print("ℹ️ System user already exists.")
