import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse

from accounts.models import CustomUser

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def subscription_page(request):
    return render(request, 'subscriptions/subscription_page.html', {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

@login_required
@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            # Check if the user already has a Stripe customer ID
            if request.user.stripe_customer_id:
                customer_id = request.user.stripe_customer_id
            else:
                # If not, create a new customer
                customer = stripe.Customer.create(email=request.user.email)
                customer_id = customer.id
                # Save the new customer ID to the user model
                request.user.stripe_customer_id = customer_id
                request.user.save()

            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
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
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def success(request):
    return render(request, 'subscriptions/success.html')

@login_required
def cancel(request):
    return render(request, 'subscriptions/cancel.html')

@require_POST
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
    # Get the subscription object from the event
    subscription = event['data']['object']

    # Get the customer ID from the subscription
    customer_id = subscription['customer']

    try:
        # Find the user with this Stripe customer ID
        user = CustomUser.objects.get(stripe_customer_id=customer_id)

        # Update the user's subscription status
        user.subscription_status = 'active'

        # You might want to store additional information about the subscription
        user.stripe_subscription_id = subscription['id']
        user.subscription_plan = subscription['plan']['nickname']
        user.subscription_current_period_end = datetime.fromtimestamp(subscription['current_period_end'])

        user.save()

        # Log it
        print(f"Subscription created for user {user.username}")

    except CustomUser.DoesNotExist:
        print(f"No user found with Stripe customer ID {customer_id}")
    except Exception as e:
        print(f"Error processing subscription creation: {str(e)}")
    pass

def handle_subscription_deleted(event):
    # Update user's subscription status
    pass