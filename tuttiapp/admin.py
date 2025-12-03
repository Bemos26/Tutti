from django.contrib import admin # Import the admin module used to register models in the admin interface
from .models import User, Lesson, MpesaTransaction # Import the models we defined in models.py
from django.contrib.auth.admin import UserAdmin # Import this!

# This makes the User model visible
# Register the custom User model so it appears in the admin interface
# Register User with UserAdmin so passwords get hashed
admin.site.register(User, UserAdmin)

# This makes the Lesson model visible and adds some filters
@admin.register(Lesson) # Register the Lesson model with custom admin options
class LessonAdmin(admin.ModelAdmin):
    list_display = ('topic', 'teacher', 'student', 'start_time', 'status')
    list_filter = ('status', 'start_time')
    search_fields = ('topic', 'student__username')

# This makes the M-Pesa transactions visible
@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'amount', 'is_successful', 'mpesa_receipt_number')