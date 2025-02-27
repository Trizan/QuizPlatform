from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Quiz, QuizAttempt, UserProfile, Notification, Topic, Category 
from .forms import QuizForm, AccountUpdateForm, UserLoginForm, UserRegistrationForm, ProfileEditForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import logout, login, authenticate, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
import random
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_POST
import json
from django.conf import settings
import requests
import time
import os
from .daily_quizzes_generator import get_quiz_from_awan_api
#from transformers import pipeline

class TooManyAttemptsError(Exception):
    pass

class CategoryListView(ListView):
    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here
        return context


#landing page
def landing_page(request):
    context = {
        'stats': [
            {
                'value': '1M+',
                'label': 'Active Learners',
                'icon': 'images/icons/users.svg'
            },
            {
                'value': '50K+',
                'label': 'Custom Quizzes',
                'icon': 'images/icons/book.svg'
            },
            {
                'value': '98%',
                'label': 'Success Rate',
                'icon': 'images/icons/trending-up.svg'
            }
        ],
        'features': [
            {
                'icon': 'images/icons/brain.svg',
                'title': 'Adaptive Learning',
                'description': 'Our AI-powered system adapts to your knowledge level, ensuring optimal learning progression and challenge'
            },
            {
                'icon': 'images/icons/trophy.svg',
                'title': 'Competitive Gaming',
                'description': 'Join live quiz battles, participate in weekly tournaments, and compete for top positions on global leaderboards'
            },
            {
                'icon': 'images/icons/users.svg',
                'title': 'Social Learning',
                'description': 'Create study groups, challenge friends, and collaborate on quiz creation with our vibrant community'
            },
            {
                'icon': 'images/icons/star.svg',
                'title': 'Personalized Progress',
                'description': 'Track your improvement with detailed analytics, learning paths, and achievement milestones'
            }
        ],
        'categories': [
            {'name': 'Science'},
            {'name': 'History'},
            {'name': 'Mathematics'},
            {'name': 'Literature'},
            {'name': 'Technology'},
            {'name': 'Arts'},
            {'name': 'Geography'},
            {'name': 'Sports'},
            {'name': 'Music'},
            {'name': 'General Knowledge'}
        ],
        'testimonials': [
            {
                'name': 'Sarah Johnson',
                'role': 'Medical Student',
                'image': 'images/testimonials/sarah.jpg',
                'quote': 'QuizPlatform has revolutionized how I prepare for my medical exams. The adaptive learning system and diverse question bank have significantly improved my test scores.'
            },
            {
                'name': 'James Chen',
                'role': 'Software Engineer',
                'image': 'images/testimonials/james.jpg',
                'quote': 'The technology-focused quizzes and competitive features keep me engaged while learning. It\'s the perfect blend of education and entertainment.'
            },
            {
                'name': 'Emily Rodriguez',
                'role': 'High School Teacher',
                'image': 'images/testimonials/emily.jpg',
                'quote': 'As an educator, I\'ve found QuizPlatform to be an invaluable tool for my students. The analytics help me identify areas where they need additional support.'
            }
        ],
        'footer_sections': [
            {
                'title': 'Product',
                'links': [
                    {'text': 'Features', 'url': '#'},
                    {'text': 'Pricing', 'url': '#'},
                    {'text': 'API', 'url': '#'}
                ]
            },
            {
                'title': 'Company',
                'links': [
                    {'text': 'About', 'url': '#'},
                    {'text': 'Blog', 'url': '#'},
                    {'text': 'Careers', 'url': '#'}
                ]
            },
            {
                'title': 'Legal',
                'links': [
                    {'text': 'Privacy', 'url': '#'},
                    {'text': 'Terms', 'url': '#'},
                    {'text': 'Security', 'url': '#'}
                ]
            }
        ],
        'social_links': [
            {
                'name': 'Twitter',
                'url': '#',
                'icon': 'images/icons/twitter.svg'
            },
            {
                'name': 'GitHub',
                'url': '#',
                'icon': 'images/icons/github.svg'
            },
            {
                'name': 'LinkedIn',
                'url': '#',
                'icon': 'images/icons/linkedin.svg'
            }
        ]
    }
    return render(request, 'landing_page.html', context)

# user registration
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create regular user
            user = form.save(commit=False)
            user.save()
            
            # Update profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.topics.set(form.cleaned_data['topics']) 

            # Process selected topics if passed
            selected_topics = request.POST.get('selected_topics')
            if selected_topics:
                try:
                    topic_ids = json.loads(selected_topics)
                    topics = Topic.objects.filter(id__in=topic_ids)
                    user.userprofile.topics.set(topics)
                    user.userprofile.save()
                except Exception as e:
                    # Log error
                    pass
                    
            # Log user in
            login(request, user)
            return redirect('quiz_feed', username=user.username)
    else:
        form = UserRegistrationForm()

    # Get all available topics
    available_topics = Topic.objects.all()
    max_topics = getattr(settings, 'MAX_USER_TOPICS', 5)  # Default to 5 if not set
    
    return render(request, 'signup.html', {
        'form': form,
        'available_topics': available_topics,
        'max_topics': max_topics
    })

# user login
@csrf_protect
def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('quiz_feed', username=user.username)  # Changed from profile to quiz_feed
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, "login.html", {"form": form})

# user logout
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")

# User profile – displays basic info, quizzes created, and attempts
@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    created_quizzes = Quiz.objects.filter(creator=profile_user)
    attempted_quizzes = QuizAttempt.objects.filter(user=profile_user)
    # Compute whether the current user is following this profile
    is_following = False
    if request.user != profile_user:
        is_following = profile_user.userprofile in request.user.userprofile.following.all()
    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'created_quizzes': created_quizzes,
        'attempted_quizzes': attempted_quizzes,
        'own_profile': request.user == profile_user,
        'is_following': is_following,
    })

# Edit profile – update user bio, picture, topics, and change password if desired
@login_required
def edit_profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user and not request.user.is_superuser:
         return render(request, "403_forbidden.html", status=403)
    
    if request.method == "POST":
            profile_form = ProfileEditForm(request.POST, request.FILES, instance=user.userprofile)
            account_form = AccountUpdateForm(request.POST, instance=user)

            if "update_profile" in request.POST:
                if profile_form.is_valid() and account_form.is_valid():
                    account_form.save()
                    profile_form.save()
                    messages.success(request, "Profile updated successfully!")
                    return redirect('user_profile', username=user.username)

            elif "change_password" in request.POST:
                password_form = PasswordChangeForm(user, request.POST)
                if password_form.is_valid():
                    password_form.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Password changed successfully!")
                    return redirect('user_profile', username=user.username)
    else:
        profile_form = ProfileEditForm(instance=user.userprofile)
        account_form = AccountUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)
    
    context = {
         "profile_form": profile_form,
         "account_form": account_form,
         "password_form": password_form,
         "profile_user": user,
    }
    return render(request, "edit_profile.html", context)

# Search users by username or bio
@login_required
def search_users(request):
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)
    system_username = "System"
    temp_user_list = []
    
    if query:
        user_list = User.objects.filter(
            (Q(username__icontains=query) | 
            Q(userprofile__bio__icontains=query))
            & ~Q(username=system_username)
        ).select_related('userprofile').distinct().order_by('username')
        
        paginator = Paginator(user_list, 20)  # Increased to 20 results
        
        try:
            users = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            users = paginator.page(1)
    else:
        users = []
    
    return render(request, 'search_results.html', {
        'users': users, 
        'query': query,
        'paginator': paginator if 'paginator' in locals() else None
    })

# Toggle follow/unfollow a user
@login_required
def toggle_follow(request, username):
    if request.method == "POST":
        profile_to_follow = get_object_or_404(UserProfile, user__username=username)
        user_profile = request.user.userprofile
        if profile_to_follow in user_profile.following.all():
            user_profile.following.remove(profile_to_follow)
            Notification.objects.create(
                user=profile_to_follow.user,
                message=f"{request.user.username} unfollowed you!",
                type="warning"
            )
        else:
            user_profile.following.add(profile_to_follow)
            # Create a notification when following
            Notification.objects.create(
                user=profile_to_follow.user,
                message=f"{request.user.username} started following you!",
                type='achievement'
            )
        # Redirect back to the page from which the request was made.
        next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
        return redirect(next_url)
    return redirect('my_quizzes')

@login_required
def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = profile_user.userprofile.followers.all()
    return render(request, 'followers_list.html', {'profile_user': profile_user, 'followers': followers})

@login_required
def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    following = profile_user.userprofile.following.all()
    return render(request, 'following_list.html', {'profile_user': profile_user, 'following': following})


# Notifications
@login_required
def notifications(request, username):
    user = get_object_or_404(User, username=username)
    """
    Display all unread notifications for the current user.
    This includes both personal notifications and global notifications.
    """
    notifications = Notification.objects.filter(
        # Get notifications that are either:
        # 1. Specifically for this user OR
        # 2. Global notifications (for all users)
        Q(user=request.user) | Q(is_global=True),
        is_read=False  # Only get unread notifications
    ).order_by('-created_at')  # Most recent first
    
    return render(request, 'notifications.html', {
        'notifications': notifications,
        "profile_user": user,
    })

# Helper function to create notifications
def create_notification(user, message, is_global=False):
    """
    Helper function to create notifications.
    Can create both personal and global notifications.
    """
    Notification.objects.create(
        user=user if not is_global else None,
        message=message,
        is_global=is_global
    )

# Count notifications
# Notification count for JS updates
@login_required
def notification_count(request):
    count = Notification.objects.filter(
        Q(user=request.user) | Q(is_global=True),
        is_read=False
    ).count()
    return JsonResponse({'count': count})

class NotificationView:
    @staticmethod
    @login_required
    def notifications_view(request):
        notifications = Notification.objects.filter(
            Q(user=request.user) | Q(is_global=True)
        ).order_by('-created_at')
        
        unread_count = notifications.filter(is_read=False).count()
        
        return render(request, 'notifications.html', {
            'notifications': notifications,
            'unread_count': unread_count,
            'show_mark_all': unread_count > 0
        })

    @staticmethod
    @login_required
    @require_POST
    @csrf_protect
    def mark_notification_read(request, notification_id):
        try:
            notification = Notification.objects.get(
                Q(user=request.user) | Q(is_global=True),
                id=notification_id,
                is_read=False
            )
            
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at'])
            
            unread_count = Notification.objects.filter(
                Q(user=request.user) | Q(is_global=True),
                is_read=False
            ).count()
            
            return JsonResponse({
                'success': True,
                'unread_count': unread_count
            })
            
        except Notification.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Notification not found'
            }, status=404)

    @staticmethod
    @login_required
    @require_POST
    @csrf_protect
    def mark_all_read(request):
        Notification.objects.filter(
            Q(user=request.user) | Q(is_global=True),
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return JsonResponse({'success': True})

    @staticmethod
    @login_required
    def notification_count(request):
        count = Notification.objects.filter(
            Q(user=request.user) | Q(is_global=True),
            is_read=False
        ).count()
        
        return JsonResponse({'count': count})


# Updated leaderboard implementation
@login_required
def leaderboard(request):
    top_users = UserProfile.objects.annotate(
        correct_answers=Count('user__quizattempt', filter=Q(user__quizattempt__is_correct=True)),
        total_attempts=Count('user__quizattempt')
    ).filter(total_attempts__gte=1).order_by('-correct_answers')[:20]
    return render(request, 'leaderboard.html', {'top_users': top_users})

# Quiz generation
def generate_quiz_for_user(user):
    """
    Generates a user-specific quiz based on their selected topics using the Awan LLM API.
    """
    user_topics = user.userprofile.topics.all()
    system = get_object_or_404(User, username="System")

    if not user_topics.exists():
        return None  # No topics selected, skip quiz generation.
    
    topic = random.choice(user_topics)  # Pick a random topic
    
    # Generate quiz using Requests library to call the API
    question_data = get_quiz_from_awan_api(topic.name)

    if not question_data:
        return None  # If generation fails, return nothing

    # Create quiz specifically for this user
    quiz = Quiz.objects.create(
        title=f"{topic.name} Quiz for {user.username}",
        question=question_data["question"],
        option1=question_data["option1"],
        option2=question_data["option2"],
        option3=question_data["option3"],
        option4=question_data["option4"],
        correct_answer=question_data["answer"],
        explanation=question_data.get("explanation", ""),
        creator=system,
        topic=topic,
        is_user_specific=True,
        created_at=timezone.now()
    )
    
    # Link the quiz directly to the specific user
    quiz.target_user = user
    quiz.save()

    return question_data

# User Feed
# Quiz feed – shows quizzes based on following, topics, or daily quizzes
@login_required
def quiz_feed(request, username):
    # get system
    system = get_object_or_404(User, username="System")
    
    # Only generate quiz if viewing your own feed
    if request.user.username == username:
        user_to_generate_quiz_for = request.user
        # Check if we need to generate a new quiz (e.g., no quizzes in last 24 hours)
        last_day = timezone.now() - timedelta(days=1)
        recent_quizzes = Quiz.objects.filter(
            target_user=request.user,
            is_user_specific=True,
            created_at__gte=last_day
        ).count()
        
        if recent_quizzes < 3:
            quiz = generate_quiz_for_user(user_to_generate_quiz_for)
    
    # Get the list of users that the current user is following
    followed_users = request.user.userprofile.following.values_list('user', flat=True)
    
    # Fetch quizzes:
    # 1. From followed users (excluding your own)
    # 2. System quizzes that aren't user-specific
    # 3. Your own user-specific quizzes
    quizzes = Quiz.objects.filter(
        (Q(creator__in=followed_users) & ~Q(creator=request.user) & ~Q(is_user_specific=True)) |
        (Q(creator=system) & ~Q(is_user_specific=True)) |
        (Q(is_user_specific=True) & Q(target_user=request.user))
    ).select_related('creator', 'creator__userprofile', 'topic')\
     .prefetch_related('liked_by')\
     .distinct()\
     .order_by('-created_at')\
     .filter(is_deleted=False)
     
    # Get attempts by the current user for these quizzes
    attempted = QuizAttempt.objects.filter(user=request.user, quiz__in=quizzes)
    attempted_ids = attempted.values_list('quiz_id', flat=True)
    
    # Build a dictionary to access attempt details by quiz ID
    attempted_dict = {attempt.quiz_id: attempt for attempt in attempted}
    
    # Split quizzes into pending (unsolved) and completed (solved)
    pending_quizzes = quizzes.exclude(id__in=attempted_ids)
    completed_quizzes = quizzes.filter(id__in=attempted_ids)
    
    context = {
        'pending_quizzes': pending_quizzes,
        'completed_quizzes': completed_quizzes,
        'attempted_dict': attempted_dict, 
    }
    return render(request, 'quiz_feed.html', context)

@login_required
def submit_quiz_answer(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Prevent multiple attempts
    if QuizAttempt.objects.filter(user=request.user, quiz=quiz).exists():
        messages.warning(request, "You have already attempted this quiz.")
        return redirect('quiz_feed', username=request.user.username)

    if request.method == "POST":
        selected_answer = request.POST.get("selected_answer")
        if not selected_answer:
            messages.error(request, "Please select an answer.")
            return redirect('quiz_feed', username=request.user.username)

        is_correct = (int(selected_answer) == quiz.correct_answer)

        # Save attempt
        QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            selected_answer=int(selected_answer),
            is_correct=is_correct
        )

        # Create notification
        Notification.objects.create(
            user=request.user,
            message=f"You answered '{quiz.title}' " + 
                    ("correctly!" if is_correct else f"incorrectly. The correct answer was option {quiz.correct_answer}.")
        )

        # Show message
        if is_correct:
            messages.success(request, "✅ Correct!")
        else:
            messages.error(request, f"❌ Incorrect! The correct answer was option {quiz.correct_answer}.")

        return redirect('quiz_feed', username=request.user.username)  # Redirect back to feed
# Solve quiz – after answering, redirect to history page so profile stats update

@login_required
def solve_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if QuizAttempt.objects.filter(user=request.user, quiz=quiz).exists():
        messages.warning(request, 'You have already attempted this quiz')
        return redirect('quiz_history')
    if request.method == 'POST':
        try:
            selected_answer = int(request.POST.get('answer'))
            is_correct = (selected_answer == quiz.correct_answer)
            QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                selected_answer=selected_answer,
                is_correct=is_correct
            )
            messages.success(request, 'Correct!' if is_correct else f'Wrong! The correct answer was option {quiz.correct_answer}')
        except Exception:
            messages.error(request, 'Invalid answer selected')
        return redirect('quiz_history')
    return render(request, 'solve_quiz.html', {'quiz': quiz})

# Create Quizzes
@login_required
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.creator = request.user
            quiz.save()
            form.save_m2m()
            # Notify followers
            for follower in request.user.userprofile.followers.all():
                Notification.objects.create(
                    user=follower.user,
                    message=f"{request.user.username} created a new quiz!"
                )
            messages.success(request, "Quiz created successfully!")
            return redirect('my_quizzes')
    else:
        form = QuizForm()
    return render(request, 'create_quiz.html', {'form': form})

# Edit quiz – only allowed for creator or superuser

@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, "Quiz updated successfully!")
            return redirect('my_quizzes')
    else:
        form = QuizForm(instance=quiz)
    # Render the my_quizzes template with the edit modal open.
    quizzes = Quiz.objects.filter(is_deleted=False, creator=request.user)
    context = {
        'quizzes': quizzes,
        'modal_type': 'edit',
        'quiz_to_edit': quiz,
        'edit_quiz_form': form,
    }
    return render(request, "my_quizzes.html", context)

# Delete quiz – only allowed for creator or superuser
@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    if request.method == 'POST':
        quiz.soft_delete()
        messages.success(request, "Quiz deleted successfully!")
        return redirect('my_quizzes')
    # Render the my_quizzes template with the delete confirmation modal open.
    quizzes = Quiz.objects.filter(is_deleted=False, creator=request.user)
    context = {
        'quizzes': quizzes,
        'modal_type': 'delete',
        'quiz_to_delete': quiz,
    }
    return render(request, "my_quizzes.html", context)

# Record of created quizes
@login_required
def my_quizzes(request):
    quizzes = Quiz.objects.filter(is_deleted=False, creator=request.user)
    context = {
        "quizzes": quizzes,
        "modal_type": request.GET.get("modal_type", None),
        "quiz_to_edit": Quiz.objects.filter(id=request.GET.get("quiz_id")).first(),
        "quiz_to_delete": Quiz.objects.filter(id=request.GET.get("quiz_id")).first(),
    }
    return render(request, "my_quizzes.html", context)

# Record of attemped quizes
@login_required
def quiz_history(request):
    attempts = QuizAttempt.objects.filter(user=request.user)
    return render(request, "quiz_history.html", {"attempts": attempts})
      
# Like feature for quiz
@login_required
def toggle_like(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user in quiz.liked_by.all():
        quiz.liked_by.remove(request.user)
    else:
        quiz.liked_by.add(request.user)
    return redirect('quiz_feed', username=request.user.username)

@login_required
def completed_quizzes(request):
    # Fetch all attempts made by the user
    attempts = QuizAttempt.objects.filter(user=request.user).select_related('quiz')
    # Use a set to avoid duplicate quiz entries.
    completed_quizzes = Quiz.objects.filter(id__in=[attempt.quiz_id for attempt in attempts])
    attempted_dict = {attempt.quiz_id: attempt for attempt in attempts}
    
    context = {
        'completed_quizzes': completed_quizzes,
        'attempted_dict': attempted_dict,
    }
    return render(request, 'completed_quizzes.html', context)


# Alternative function-based view
def category_list(request):
    categories = Category.objects.filter(is_active=True).order_by('name')
    context = {
        'categories': categories,
    }
    return render(request, 'categories.html', context)
