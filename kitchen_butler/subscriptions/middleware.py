from django.shortcuts import redirect
from django.urls import reverse

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.subscription_status != 'active':
            if not request.path.startswith(reverse('subscription_page')):
                return redirect('subscription_page')
        response = self.get_response(request)
        return response