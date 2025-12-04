from django import forms
from .models import Lesson
from django.core.validators import RegexValidator

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
        
        
class LessonRescheduleForm(forms.ModelForm): # Form for rescheduling lessons. Used by teachers. 
    class Meta:
        model = Lesson
        fields = ['start_time', 'topic']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'})
        }
        
        
        


class MpesaPaymentForm(forms.Form):
    phone_number = forms.CharField(
        label="M-Pesa Number",
        max_length=15,
        help_text="Format: 07XX... or 01XX...",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0712345678'})
    )