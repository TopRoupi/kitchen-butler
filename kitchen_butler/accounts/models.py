from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=50, blank=True, null=True)
    subscription_status = models.CharField(max_length=20, default='inactive')
    subscription_plan = models.CharField(max_length=100, blank=True, null=True)
    subscription_current_period_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username