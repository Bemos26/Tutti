from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Lesson, MpesaTransaction, User
# from django_daraja.mpesa.core import MpesaClient
from .forms import LessonRequestForm

# ==========================================
# 1. THE DASHBOARD (Home Base)
# ==========================================
@login_required
def dashboard(request):
    user = request.user
    
    # Logic: Filter lessons based on who is logged in
    if user.is_teacher:
        my_lessons = Lesson.objects.filter(teacher=user).order_by('start_time')
    elif user.is_student:
        my_lessons = Lesson.objects.filter(student=user).order_by('start_time')
    else:
        my_lessons = Lesson.objects.none()

    context = {
        'lessons': my_lessons
    }
    
    return render(request, 'tuttiapp/dashboard.html', context)


# ==========================================
# 2. MARKETPLACE (Find & Request Teachers)
# ==========================================
@login_required
def teacher_list(request):
    """Displays a list of all users marked as teachers."""
    teachers = User.objects.filter(is_teacher=True)
    return render(request, 'tuttiapp/teacher_list.html', {'teachers': teachers})

@login_required
def request_lesson(request, teacher_id):
    """Handles the form where a student requests a lesson."""
    target_teacher = get_object_or_404(User, pk=teacher_id)
    
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            # Create the lesson object but don't save to DB yet
            lesson = form.save(commit=False)
            
            # Fill in the missing data
            lesson.student = request.user
            lesson.teacher = target_teacher
            lesson.status = 'REQUESTED'  # Important!
            
            lesson.save()
            
            messages.success(request, f"Request sent to {target_teacher.username}!")
            return redirect('dashboard')
    else:
        form = LessonRequestForm()

    context = {
        'form': form,
        'teacher': target_teacher
    }
    return render(request, 'tuttiapp/request_lesson.html', context)


# ==========================================
# 3. TEACHER ACTIONS (Approve/Decline)
# ==========================================
@login_required
def approve_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    # Security check: Only the assigned teacher can approve
    if request.user == lesson.teacher:
        lesson.status = 'SCHEDULED'
        lesson.save()
        messages.success(request, "Lesson Confirmed!")
    else:
        messages.error(request, "You are not authorized to approve this.")
        
    return redirect('dashboard')

@login_required
def decline_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    if request.user == lesson.teacher:
        lesson.delete() # Or you could set status to 'CANCELLED'
        messages.warning(request, "Request declined.")
        
    return redirect('dashboard')


# ==========================================
# 4. PAYMENTS (M-Pesa Integration)
# ==========================================
@login_required
def initiate_payment(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    # Check for phone number
    if not request.user.phone_number:
        messages.error(request, "Please add a phone number to your profile first!")
        return redirect('dashboard')
        
    # Setup M-Pesa Client
    client = MpesaClient()
    phone_number = request.user.phone_number
    amount = int(lesson.price)
    account_reference = f"Lesson {lesson.id}"
    transaction_desc = f"Payment for {lesson.topic}"
    callback_url = 'https://mydomain.com/callback' # We'll fix this later
    
    try:
        response = client.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
        messages.success(request, f"STK Push sent to {phone_number}. Check your phone!")
    except Exception as e:
        messages.error(request, f"Error connecting to M-Pesa: {str(e)}")
    
    return redirect('dashboard')



# ==========================================
from .forms import LessonRequestForm, LessonRescheduleForm # Import the new form for rescheduling
# 5. RESCHEDULING LESSONS

# 1. TEACHER: Change the time
@login_required
def reschedule_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    # Security: Only the teacher can reschedule
    if request.user != lesson.teacher:
        messages.error(request, "Only the conductor can reschedule.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = LessonRescheduleForm(request.POST, instance=lesson)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.status = 'RESCHEDULE_PENDING' # Change status so student sees it
            lesson.save()
            messages.success(request, "Reschedule proposal sent to student.")
            return redirect('dashboard')
    else:
        # Pre-fill the form with the current data
        form = LessonRescheduleForm(instance=lesson)

    return render(request, 'tuttiapp/reschedule_form.html', {'form': form, 'lesson': lesson})

# 2. STUDENT: Accept the new time
@login_required
def accept_reschedule(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    if request.user == lesson.student:
        lesson.status = 'SCHEDULED' # Make it official again
        lesson.save()
        messages.success(request, "New time accepted!")
    
    return redirect('dashboard')