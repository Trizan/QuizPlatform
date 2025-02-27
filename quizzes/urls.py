from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('signup/', views.register, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('notifications/count/', views.notification_count, name='notification_count'),
    path('generate_quizzes/', views.generate_quiz_for_user, name='generate_quizzes'),
    path('about/', views.landing_page, name='about'),
    path('contact/', views.landing_page, name='contact'),
    path('privacy/', views.landing_page, name='privacy'),
    path('terms/', views.landing_page, name='terms'),

    # Unique user-based URLs
    path('<str:username>/quiz_feed/', views.quiz_feed, name='quiz_feed'),
    path('<str:username>/notifications/', views.notifications, name='notifications'),
    path('<str:username>/profile/', views.user_profile, name='user_profile'),
    path('<str:username>/settings/', views.edit_profile, name='edit_profile'),
    path('<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('<str:username>/followers/', views.followers_list, name='followers_list'),
    path('<str:username>/following/', views.following_list, name='following_list'),
    

    # Quiz-related URLs
    path('quiz/create/', views.create_quiz, name='create_quiz'),
    path('quiz/<int:quiz_id>/', views.solve_quiz, name='solve_quiz'),
    path('quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('quiz/<int:quiz_id>/like/', views.toggle_like, name='toggle_like'),
    path('submit-quiz-answer/<int:quiz_id>/', views.submit_quiz_answer, name='submit_quiz_answer'),

    path('completed/', views.completed_quizzes, name='completed_quizzes'),


    # User dashboards and leaderboards
    path('myquizzes/', views.my_quizzes, name='my_quizzes'),
    path('history/', views.quiz_history, name='quiz_history'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),

    # Search
    path('search/', views.search_users, name='search_users'),

    # Notifications
    # Action endpoints
    path('notifications/<int:notification_id>/mark-read/', 
         views.NotificationView.mark_notification_read, 
         name='mark_notification_read'),
    path('notifications/mark-all-read/', 
         views.NotificationView.mark_all_read, 
         name='mark_all_read'),

    # Password reset views
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name="password_reset_confirm"),
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name="password_reset_complete"),
    path("password-change/", auth_views.PasswordChangeView.as_view(template_name="password_change.html"), name="password_change"),
    path("password-change/done/", auth_views.PasswordChangeDoneView.as_view(template_name="password_change_done.html"), name="password_change_done"),
] 
