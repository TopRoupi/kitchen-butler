from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        return render(request, 'pages/dashboard.html')
    else:
        return render(request, 'pages/landing.html')
    
@login_required
def dashboard(request):
    # You can add context data here as needed
    context = {
        'user': request.user,
    }
    return render(request, 'pages/dashboard.html', context)