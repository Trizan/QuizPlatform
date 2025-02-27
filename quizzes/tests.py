from django.test import TestCase
from django.contrib.auth.models import User
from .models import Quiz, Topic
from datetime import datetime

class QuizTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser', password='password')
        topic = Topic.objects.create(name='Science')
        Quiz.objects.create(
            title='Sample Quiz',
            question='What is 2+2?',
            option1='3',
            option2='4',
            option3='5',
            option4='6',
            correct_answer='4',
            creator=user,
            topic=topic,
            created_at=datetime.now(),
        )

    def test_quiz_creation(self):
        quiz = Quiz.objects.get(title='Sample Quiz')
        self.assertEqual(quiz.correct_answer, '4')
