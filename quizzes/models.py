from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='profile_pics/', default='default_avatars/avatar_1.jpg')
    topics = models.ManyToManyField(Topic, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    # New sensitive fields
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    # Privacy flags: if True, display on public profile
    show_address = models.BooleanField(default=False)
    show_phone_number = models.BooleanField(default=False)
    email_public = models.BooleanField(default=False)
    
    
    def quiz_count(self):
        return self.user.quiz_set.count()

    def attempt_count(self):
        return self.user.quizattempt_set.count()

    def correct_count(self):
        return self.user.quizattempt_set.filter(is_correct=True).count()

    def success_rate(self):
        attempts = self.attempt_count()
        return (self.correct_count() / attempts * 100) if attempts > 0 else 0

    def follower_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

@receiver(post_save, sender=User)
def create_or_update_userprofile(sender, instance, created, **kwargs):
    if created or not hasattr(instance, "userprofile"):
        UserProfile.objects.get_or_create(user=instance)

class Quiz(models.Model):
    title = models.CharField(max_length=200, default='Basic Science Quiz')
    question = models.TextField(default='What is the chemical symbol for gold?')
    option1 = models.CharField(max_length=200, default='Au')
    option2 = models.CharField(max_length=200, default='Ag')
    option3 = models.CharField(max_length=200, default='Fe')
    option4 = models.CharField(max_length=200, default='Cu')
    correct_answer = models.IntegerField(choices=[(1, 'Option 1'), (2, 'Option 2'),
                                                    (3, 'Option 3'), (4, 'Option 4')], default=1)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_daily = models.BooleanField(default=False)
    liked_by = models.ManyToManyField(User, related_name="liked_quizzes", blank=True)
    explanation = models.TextField(blank=True, null=True, 
                                 help_text="Provide an explanation for the correct answer")
    is_deleted = models.BooleanField(default=False)  # Soft delete flag
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_user_specific = models.BooleanField(default=False)
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, 
                                    null=True, blank=True, 
                                    related_name="targeted_quizzes")

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        ordering = ['-created_at']

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey("Quiz", on_delete=models.SET_NULL, null=True)
    selected_answer = models.IntegerField()
    is_correct = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'quiz']  # Prevents multiple attempts

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({'Correct' if self.is_correct else 'Incorrect'})"

class Notification(models.Model):
    TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('achievement', 'Achievement')
    ]
    type = models.CharField(max_length=20, choices=TYPES, default='info')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_global = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.message} - {'Global' if self.is_global else self.user.username}"

    @classmethod
    def cleanup_old_notifications(cls):
        ten_days_ago = timezone.now() - timedelta(days=10)
        cls.objects.filter(created_at__lt=ten_days_ago).delete()

class DeletedQuiz(models.Model):
    title = models.CharField(max_length=200)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    deleted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Deleted Quiz: {self.title}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def quiz_count(self):
        return self.quiz_set.count()
    
    @property
    def total_questions(self):
        return sum(quiz.questions.count() for quiz in self.quiz_set.all())
