from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
import re

#EVERY TIME YOU ADD A NEW MODE MAKE SURE TO RUN:
# python manage.py makemigrations
# python manage.py migrate

# --- 1. THE HELPER (Phone Sanitizer) ---
# This ensures that if a user enters "0712..." it saves as "254712..."
def validate_kenyan_phone(value):
    value = str(value).replace("+", "").replace(" ", "").replace("-", "")
    if value.startswith("07") or value.startswith("01"):
        value = "254" + value[1:]
    if not re.match(r"^254\d{9}$", value):
        raise ValidationError(f"{value} is not a valid M-Pesa number. Use format 2547XXXXXXXX")
    return value

# --- 2. THE USER (Teachers & Students) ---
class User(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True, validators=[validate_kenyan_phone])

# --- 3. THE LESSON (The Core Logic) ---
class Lesson(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),  # Student requested a lesson
        ('SCHEDULED', 'Scheduled'),
        ('RESCHEDULE_PENDING', 'Reschedule Pending'), # Teacher requested reschedule
        ('COMPLETED', 'Completed'),       # Lesson happened, teacher marked it
        ('PENDING_PAYMENT', 'Pending Payment'), # Waiting for M-Pesa
        ('PAID', 'Paid'),                 # Money received
        ('CANCELLED', 'Cancelled'),
    ]

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lessons_taught')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lessons_taken')
    
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    
    topic = models.CharField(max_length=200, help_text="What are you teaching? e.g. Major Scales")
    teacher_notes = models.TextField(blank=True, help_text="Notes for the student to practice")
    
    price = models.DecimalField(max_digits=8, decimal_places=2, default=1500.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    # Reminders (For later use)
    is_student_reminder_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.topic} ({self.student.username})"

# --- 4. THE MONEY (M-Pesa) ---
class MpesaTransaction(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='transaction')
    checkout_request_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_receipt_number = models.CharField(max_length=20, blank=True, null=True)
    is_successful = models.BooleanField(default=False)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tx for Lesson {self.lesson.id}"