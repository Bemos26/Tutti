import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutti.settings')
django.setup()

from tuttiapp.models import User, Lesson
from django.utils import timezone
import datetime

def setup():
    # Create Teacher
    if not User.objects.filter(username='maestro').exists():
        User.objects.create_user(username='maestro', password='password123', is_teacher=True, phone_number='0711111111')
        print("Created teacher: maestro")
    
    # Create Student
    if not User.objects.filter(username='student1').exists():
        User.objects.create_user(username='student1', password='password123', is_student=True, phone_number='0722222222')
        print("Created student: student1")

    # Create Lesson
    teacher = User.objects.get(username='maestro')
    student = User.objects.get(username='student1')
    
    if not Lesson.objects.filter(teacher=teacher, student=student).exists():
        Lesson.objects.create(
            teacher=teacher, 
            student=student, 
            topic="Intro to Piano", 
            start_time=timezone.now() + datetime.timedelta(days=1),
            status='REQUESTED'
        )
        print("Created lesson: Intro to Piano")

if __name__ == '__main__':
    setup()
