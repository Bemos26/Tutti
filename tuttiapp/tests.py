from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Lesson
from django.utils import timezone
import datetime

User = get_user_model()

class ModelsTestCase(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='password', is_teacher=True, phone_number='0712345678')
        self.student = User.objects.create_user(username='student', password='password', is_student=True, phone_number='0787654321')

    def test_user_creation(self):
        self.assertEqual(self.teacher.username, 'teacher')
        self.assertTrue(self.teacher.is_teacher)
        # Check phone validation
        self.assertEqual(self.teacher.phone_number, '254712345678')

    def test_lesson_creation(self):
        lesson = Lesson.objects.create(
            teacher=self.teacher,
            student=self.student,
            start_time=timezone.now() + datetime.timedelta(days=1),
            topic="Piano Basics"
        )
        self.assertEqual(lesson.status, 'SCHEDULED')
        self.assertEqual(lesson.price, 1500.00)

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(username='teacher', password='password', is_teacher=True)
        self.admin = User.objects.create_superuser(username='admin', password='password', email='admin@example.com')

    def test_dashboard_login_required(self):
        response = self.client.get(reverse('dashboard'))
        self.assertNotEqual(response.status_code, 200) # Should redirect to login

    def test_dashboard_access(self):
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_manage_users_admin_only(self):
        # Teacher tries to access admin page
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('manage_users'))
        # Should be 302 redirect (due to user_passes_test) or 403 depending on config.
        # But user_passes_test redirects to login by default if test fails and login_url not set?
        # Actually user_passes_test redirects to login_url. 
        # If logged in but fails test, it might redirect or 403. 
        # Django's user_passes_test redirects to login with ?next= if false.
        self.assertEqual(response.status_code, 302) 

        # Admin accesses admin page
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('manage_users'))
        self.assertEqual(response.status_code, 200)
