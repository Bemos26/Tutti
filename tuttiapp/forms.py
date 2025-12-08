from django import forms
from .models import Lesson
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm
from .models import User


#i created this form to handle lesson requests by students
#it uses django's ModelForm to automatically generate form fields based on the Lesson model

class LessonRequestForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['topic', 'start_time']
        widgets = {
            # This makes a nice calendar popup in the browser
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Jazz Piano Basics'})
        }
        '''
        This form captures the topic and start time for a lesson request made by a student.
        It uses HTML5 input types for better user experience.
        The form is displayed when a student wants to request a new lesson.
        '''
        
        
class LessonRescheduleForm(forms.ModelForm): # Form for rescheduling lessons. Used by teachers. 
    class Meta:
        model = Lesson
        fields = ['start_time', 'topic']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'})
        }
        
        '''
        This form allows teachers to reschedule a lesson by changing the start time and topic.
        The form is displayed when a teacher wants to reschedule an existing lesson.
        '''
class MpesaPaymentForm(forms.Form): # Form to capture M-Pesa payment details
    phone_number = forms.CharField(
        label="M-Pesa Number",
        max_length=15,
        help_text="Format: 07XX... or 01XX...",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0712345678'})
    )
    '''
    this form captures the phone number used for M-Pesa payments.
    It includes validation to ensure the number is in the correct format.
    it is displayed when a student is making a payment for a lesson.
    
    '''
    
    

class TuttiSignUpForm(UserCreationForm): # Custom user registration form with role selection and M-Pesa fields. it is displayed during user signup.
    # Add a dropdown for the user to pick their role
    ROLE_CHOICES = [
        ('student', 'Performer (Student)'),
        ('teacher', 'Conductor (Teacher)'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, label="I am a:")
    '''
    This form extends the default UserCreationForm to include a role selection (student or teacher)
    and additional fields for M-Pesa phone number and email.
    It is used during user registration to capture all necessary information.
    '''
    
    # Add the M-Pesa fields
    phone_number = forms.CharField(
        max_length=15, 
        required=True, 
        help_text="Required for M-Pesa. Format: 07XX... or 01XX..."
    )
    email = forms.EmailField(required=True)
    

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'first_name', 'last_name']

    def save(self, commit=True):
        # 1. Save the basic user info (username/password)
        user = super().save(commit=False)
        
        # 2. Set the "is_teacher" or "is_student" flag based on the dropdown
        role = self.cleaned_data.get('role')
        if role == 'teacher':
            user.is_teacher = True
            user.is_student = False
        else:
            user.is_student = True
            user.is_teacher = False
            
        # 3. Save to database
        if commit:
            user.save()
        return user