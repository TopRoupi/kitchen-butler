from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        return render(request, 'pages/home.html')
    else:
        return render(request, 'pages/landing.html')