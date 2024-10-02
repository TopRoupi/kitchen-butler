from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
import stripe
from django.conf import settings

stripe.api_KEY = settings.STRIPE_SECRET_KEY

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create Stripe customer
            customer = stripe.Customer.create(email=user.email)
            user.stripe_customer_id = customer.id
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})