"""
URL configuration for tutti project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include #make sure you also inport views so that this file is able to detect the functions in other appslike tuttiapp
from tuttiapp import views  # Import your views here. Make sure to import the views module because it contails the dashboard function

urlpatterns = [
    path('admin/', admin.site.urls), #this is default and it contains the admin controls ie the superuser
    
    
    
    # When someone visits the homepage (''), call the dashboard view
    path('', views.dashboard, name='dashboard'), # this means that dashboard is the homepage
    
    
    
    #It enables /accounts/login/ and /accounts/logout/
    path('accounts/', include('django.contrib.auth.urls')),
    
    
    path('teachers/', views.teacher_list, name='teacher_list'), # New URL pattern for listing teachers
    path('request/<int:teacher_id>/', views.request_lesson, name='request_lesson'), # New URL pattern for requesting a lesson
    path('approve/<int:lesson_id>/', views.approve_lesson, name='approve_lesson'), # New URL pattern for approving a lesson
    path('decline/<int:lesson_id>/', views.decline_lesson, name='decline_lesson'), # New URL pattern for declining a lesson
    path('reschedule/<int:lesson_id>/', views.reschedule_lesson, name='reschedule_lesson'), # New URL pattern for rescheduling a lesson
    path('accept-reschedule/<int:lesson_id>/', views.accept_reschedule, name='accept_reschedule'), # New URL pattern for accepting a reschedule
    path('pay/<int:lesson_id>/', views.initiate_payment, name='initiate_payment'), # New URL pattern for initiating payment
    
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'), # New URL pattern for M-Pesa callback
    
    path('complete/<int:lesson_id>/', views.complete_lesson, name='complete_lesson'), # New URL pattern for completing a lesson
    
    path('mark-paid/<int:lesson_id>/', views.mark_lesson_paid, name='mark_lesson_paid'), # New URL pattern for marking a lesson as paid
    
    path('signup/', views.signup, name='signup'), # New URL pattern for user signup.html page that handles both student and teacher signups
    path('delete/<int:lesson_id>/', views.delete_lesson, name='delete_lesson'), # New URL pattern for deleting a lesson
    
    path('admin-panel/users/', views.manage_users, name='manage_users'),
    path('admin-panel/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

]

#make sure that all the views that are found in views.py are defined here for them to work
#remember you dont have to have two seperate url.py files, just use this one on the parent folder tutti to define all the urls
