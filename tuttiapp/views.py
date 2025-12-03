from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Lesson

@login_required # Ensure the user is logged in to access the dashboard
def dashboard(request):
    user = request.user
    
    # Logic: 
    # 1. If I am a teacher, find lessons where I am the 'teacher'
    # 2. If I am a student, find lessons where I am the 'student'
    
    if user.is_teacher:
        my_lessons = Lesson.objects.filter(teacher=user)
    elif user.is_student:
        my_lessons = Lesson.objects.filter(student=user)
    else:
        # If I am neither (e.g. just an admin), show nothing
        my_lessons = Lesson.objects.none()

    # context is the package of data we send to the HTML
    context = {
        'lessons': my_lessons
    }
    
    return render(request, 'tuttiapp/dashboard.html', context) #this means we dont have to have a seperate urls in the tuttiapp. we can add all the urls directly to the urls file that already exists in the main project folder