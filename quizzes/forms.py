# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Quiz, Topic
from django.db.models import Q
from django.conf import settings
import os, random
from .models import QuizAttempt

'''
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select up to 5 topics"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Try logging in instead.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists. Try logging in instead.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            if hasattr(user_profile, "topics"):
                user_profile.selected_topics.set(self.cleaned_data["topics"])
        return user
'''

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    topics = forms.ModelMultipleChoiceField(
         queryset=Topic.objects.all(),
         widget=forms.CheckboxSelectMultiple,
         required=True,
         help_text="Select topics you're interested in"
    )
    avatar = forms.ImageField(required=False)
    
    class Meta:
         model = User
         fields = ["username", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            user.userprofile.topics.set(self.cleaned_data["topics"])
            # Set avatar if provided
            if self.cleaned_data.get("avatar"):
                user.userprofile.avatar = self.cleaned_data.get("avatar")
            else:
                # Try to set a random default avatar
                default_folder = os.path.join(settings.MEDIA_ROOT, 'default_avatars')
                print(f"Default folder path: {default_folder}")
                print(f"Does folder exist: {os.path.exists(default_folder)}")
                if os.path.exists(default_folder):
                    choices = os.listdir(default_folder)
                    print(f"Available avatar choices: {choices}")
                try:
                    if os.path.exists(default_folder):
                        choices = os.listdir(default_folder)
                        if choices:
                            random_choice = random.choice(choices)
                            user.userprofile.avatar = f'default_avatars/{random_choice}'
                        else:
                            # Fallback to a specific default if directory is empty
                            user.userprofile.avatar = 'default_avatars/avatar_1.jpg'
                    else:
                        # Fallback if directory doesn't exist
                        user.userprofile.avatar = 'default_avatars/avatar_1.jpg'

                    # Log that we're using the default avatar
                    print(f"Using default avatar: {user.userprofile.avatar}")
                except Exception as e:
                    # Log any errors that occur
                    print(f"Error setting default avatar: {e}")
                    user.userprofile.avatar = 'default_avatars/avatar_1.jpg'

            user.userprofile.save()
        return user

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'bio', 
            'avatar', 
            'topics', 
            'address', 
            'phone_number', 
            'show_address', 
            'show_phone_number',
            'email_public'
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topics'].widget = forms.CheckboxSelectMultiple()
        self.fields['topics'].queryset = Topic.objects.all()

class QuizForm(forms.ModelForm):
    correct_answer = forms.ChoiceField(
        choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')],
        widget=forms.RadioSelect
    )
    explanation = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text="Optional explanation for the correct answer"
    )
    
    class Meta:
        model = Quiz
        fields = ('title', 'question', 'option1', 'option2', 'option3', 'option4', 
                  'correct_answer', 'topic', 'explanation')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500'
            })

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

class UserProfileForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = UserProfile
        fields = ('bio', 'avatar', 'topics')

class AccountUpdateForm(forms.ModelForm):
    class Meta:
         model = User
         fields = ['username', 'email']
    def clean_username(self):
         username = self.cleaned_data.get('username')
         if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
              raise forms.ValidationError("This username is already taken.")
         return username

class QuizAttemptForm(forms.Form):
    selected_answer = forms.ChoiceField(
        choices=[(1, "Option 1"), (2, "Option 2"), (3, "Option 3"), (4, "Option 4")],
        widget=forms.RadioSelect
    )





    