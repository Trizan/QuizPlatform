from django.contrib import admin
from .models import Topic, UserProfile, Quiz, QuizAttempt, Notification, Category

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register your other models
admin.site.register(UserProfile)
admin.site.register(Quiz)
admin.site.register(QuizAttempt)
admin.site.register(Notification)
admin.site.register(Category)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'quiz_count', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    def quiz_count(self, obj):
        return obj.quiz_count
    quiz_count.short_description = 'Number of Quizzes'

