from django.contrib import admin # Import the admin module used to register models in the admin interface
from .models import User, Lesson, MpesaTransaction # Import the models we defined in models.py
from django.contrib.auth.admin import UserAdmin # Import this! it provides a lot of functionality for managing users as admin

# This makes the User model visible
# Register the custom User model so it appears in the admin interface
# Register User with UserAdmin so passwords get hashed
admin.site.register(User, UserAdmin)

# This makes the Lesson model visible and adds some filters
@admin.register(Lesson) # Register the Lesson model with custom admin options
class LessonAdmin(admin.ModelAdmin):
    list_display = ('topic', 'teacher', 'student', 'start_time', 'status') # Fields to display in the admin list view
    list_filter = ('status', 'start_time') # Add filters for status and start time
    search_fields = ('topic', 'student__username') # Enable search by topic and student username

# This makes the M-Pesa transactions visible
@admin.register(MpesaTransaction) # Register the MpesaTransaction model with custom admin options
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'amount', 'is_successful', 'mpesa_receipt_number') # Fields to display in the admin list view