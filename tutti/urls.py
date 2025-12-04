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
from django.urls import path, include
from tuttiapp import views  # Import your views here. Make sure to import the views module because it contails the dashboard function

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # When someone visits the homepage (''), call the dashboard view
    path('', views.dashboard, name='dashboard'), # this means that dashboard is the homepage
    
    #It enables /accounts/login/ and /accounts/logout/
    path('accounts/', include('django.contrib.auth.urls')),
    
    
    path('teachers/', views.teacher_list, name='teacher_list'), # New URL pattern for listing teachers
    path('request/<int:teacher_id>/', views.request_lesson, name='request_lesson'), # New URL pattern for requesting a lesson
    path('approve/<int:lesson_id>/', views.approve_lesson, name='approve_lesson'), # New URL pattern for approving a lesson
    path('decline/<int:lesson_id>/', views.decline_lesson, name='decline_lesson'), # New URL pattern for declining a lesson
]