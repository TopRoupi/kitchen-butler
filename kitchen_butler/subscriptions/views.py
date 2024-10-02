from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def subscription_page(request):
    return render(request, 'subscriptions/subscription_page.html', {'stripe_public_key': settings.STRIPE_PUBLIC_KEY})

@login_required
def create_checkout_session(request):
    checkout_session = stripe.checkout.Session.create(
        customer=request.user.stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': settings.STRIPE_PRICE_ID,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=request.build_absolute_uri('/subscriptions/success/'),
        cancel_url=request.build_absolute_uri('/subscriptions/cancel/'),
    )
    return JsonResponse({'id': checkout_session.id})

@login_required
def success(request):
    return render(request, 'subscriptions/success.html')

@login_required
def cancel(request):
    return render(request, 'subscriptions/cancel.html')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    if event['type'] == 'customer.subscription.created':
        handle_subscription_created(event)
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event)

    return HttpResponse(status=200)

def handle_subscription_created(event):
    # Update user's subscription status
    pass

def handle_subscription_deleted(event):
    # Update user's subscription status
    pass