from django.shortcuts import render, get_object_or_404, redirect 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Lesson, MpesaTransaction, User
from django_daraja.mpesa.core import MpesaClient
from .forms import LessonRequestForm

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import MpesaPaymentForm
from .models import validate_kenyan_phone

from django.db.models import Sum, Count
from django.db.models import Q # For search queries

# ==========================================
# 1. THE DASHBOARD (Home Base)
# ==========================================
@login_required
def dashboard(request):
    user = request.user
    context = {}

    # === SCENARIO 1: THE SUPERUSER (Admin) ===
    if user.is_superuser:
        # 1. High Level Stats
        total_students = User.objects.filter(is_student=True).count()
        total_teachers = User.objects.filter(is_teacher=True).count()
        
        # Calculate Revenue (Sum of successful M-Pesa transactions)
        # We use 'aggregate' which returns a dictionary like {'amount__sum': 5000}
        revenue_data = MpesaTransaction.objects.filter(is_successful=True).aggregate(Sum('amount'))
        total_revenue = revenue_data['amount__sum'] or 0
        
        # 2. Recent Data for the Tables
        recent_transactions = MpesaTransaction.objects.all().order_by('-transaction_date')[:5]
        recent_users = User.objects.all().order_by('-date_joined')[:5]
        
        context = {
            'is_admin': True, # Flag to tell template to show Admin Mode
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_revenue': total_revenue,
            'recent_transactions': recent_transactions,
            'recent_users': recent_users,
        }

    # === SCENARIO 2: THE TEACHER ===
    elif user.is_teacher:
        my_lessons = Lesson.objects.filter(teacher=user).order_by('start_time')
        context = {'lessons': my_lessons}

    # === SCENARIO 3: THE STUDENT ===
    elif user.is_student:
        my_lessons = Lesson.objects.filter(student=user).order_by('start_time')
        context = {'lessons': my_lessons}

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


# ==================================
# ==================================
    



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


# 1. THE PAYMENT PAGE (Show Form & Trigger STK)
@login_required
def initiate_payment(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    if request.method == 'POST':
        form = MpesaPaymentForm(request.POST)
        if form.is_valid():
            raw_phone = form.cleaned_data['phone_number']
            
            try:
                # 1. Sanitize the phone number (07XX -> 2547XX)
                phone_number = validate_kenyan_phone(raw_phone)
                
                # 2. Setup M-Pesa Client
                client = MpesaClient()
                amount = int(lesson.price)
                account_reference = f"Tutti-{lesson.id}"
                transaction_desc = f"Lesson: {lesson.topic}"
                
                # IMPORTANT: This URL must be accessible from the internet
                callback_url = 'https://tutti-pnpn.onrender.com/mpesa/callback/'  # Replace with your actual callback URL. i have just used a dummy one here.
                
                # 3. Fire STK Push
                response = client.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
                
                # 4. Save the Checkout Request ID to track the payment
                # Note: response is an object, we access attributes directly
                if response.response_code == '0':
                    MpesaTransaction.objects.create(
                        lesson=lesson,
                        checkout_request_id=response.checkout_request_id,
                        phone_number=phone_number,
                        amount=amount
                    )
                    messages.success(request, f"STK Push sent to {phone_number}. Enter your PIN!")
                else:
                    messages.error(request, f"M-Pesa Error: {response.response_description}")

                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        # Pre-fill with user's profile number if it exists
        initial_data = {'phone_number': request.user.phone_number} if request.user.phone_number else {}
        form = MpesaPaymentForm(initial=initial_data)

    return render(request, 'tuttiapp/pay_confirm.html', {'form': form, 'lesson': lesson})


# 2. THE CALLBACK (Safaricom talks to us)
@csrf_exempt # Safaricom doesn't have our CSRF token, so we exempt this view
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            # 1. Parse the JSON response
            body = json.loads(request.body)
            stk_callback = body.get('Body', {}).get('stkCallback', {})
            
            result_code = stk_callback.get('ResultCode')
            checkout_id = stk_callback.get('CheckoutRequestID')
            result_desc = stk_callback.get('ResultDesc')

            # 2. Find the transaction
            transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_id)
            
            # 3. Update Transaction Status
            if result_code == 0:
                # Success!
                transaction.is_successful = True
                transaction.result_desc = "Payment Successful"
                
                # Extract Receipt Number
                items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in items:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        transaction.mpesa_receipt_number = item.get('Value')
                
                transaction.save()
                
                # 4. MARK LESSON AS PAID
                lesson = transaction.lesson
                lesson.status = 'PAID'
                lesson.save()
            else:
                # User cancelled or failed
                transaction.is_successful = False
                transaction.result_desc = result_desc
                transaction.save()
                
        except Exception as e:
            print(f"Callback Error: {e}")
            
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


@login_required
def complete_lesson(request, lesson_id):
    """
    Teacher marks the lesson as finished.
    This triggers the status change to PENDING_PAYMENT,
    which reveals the Pay button to the student.
    """
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    # Security: Only the teacher can do this
    if request.user == lesson.teacher:
        lesson.status = 'PENDING_PAYMENT'
        lesson.save()
        messages.success(request, "Lesson marked as Complete. Payment requested from student.")
    else:
        messages.error(request, "You are not authorized to manage this lesson.")
        
    return redirect('dashboard')



@login_required
def mark_lesson_paid(request, lesson_id):
    """
    Manual override for cash payments or testing.
    Only the Teacher can perform this.
    """
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    if request.user == lesson.teacher:
        lesson.status = 'PAID'
        lesson.save()
        messages.success(request, "Payment recorded manually (Cash/Test).")
    else:
        messages.error(request, "Not authorized.")
        
    return redirect('dashboard')




from django.contrib.auth import login
from .forms import TuttiSignUpForm # Import the new class in froms.py that allows user signup

def signup(request):
    if request.method == 'POST':
        form = TuttiSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately
            login(request, user)
            messages.success(request, "Welcome to Tutti! Your account is ready.")
            return redirect('dashboard')
    else:
        form = TuttiSignUpForm()
    
    return render(request, 'registration/signup.html', {'form': form})



@login_required
def delete_lesson(request, lesson_id): # Delete a lesson that is no longer needed to avoid cluttering the dashboard
    """
    Allows the teacher to permanently remove a lesson.
    """
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    # Security: Only the assigned teacher can delete
    if request.user == lesson.teacher:
        lesson.delete()
        messages.success(request, "Lesson deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this.")
        
    return redirect('dashboard')





@login_required
def manage_users(request):
    """
    Admin-only page to view and manage all users.
    """
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admins only.")
        return redirect('dashboard')

    # Get search term (if any)
    query = request.GET.get('q')
    
    if query:
        # Search by username, email, or phone
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) | 
            Q(phone_number__icontains=query)
        ).order_by('-date_joined')
    else:
        users = User.objects.all().order_by('-date_joined')

    return render(request, 'tuttiapp/manage_users.html', {'users': users, 'search_term': query})

@login_required
def delete_user(request, user_id):
    """
    Admin-only function to delete a specific user.
    """
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    user_to_delete = get_object_or_404(User, pk=user_id)
    
    # Prevent admin from deleting themselves!
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own admin account!")
        return redirect('manage_users')
        
    username = user_to_delete.username
    user_to_delete.delete()
    messages.success(request, f"User '{username}' has been deleted.")
    
    return redirect('manage_users')