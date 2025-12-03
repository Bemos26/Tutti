from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# This function handles the dashboard page
def dashboard(request):
    # 'request' contains info about the current user
    return render(request, 'tuttiapp/dashboard.html') #this means we dont have to have a seperate urls in the tuttiapp. we can add all the urls directly to the urls file that already exists in the main project folder