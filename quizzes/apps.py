from django.apps import AppConfig


class QuizzesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quizzes'

    def ready(self):
        print("✅ QuizzesConfig ready() executed")
        import quizzes.signals  # Ensure signals are loaded

