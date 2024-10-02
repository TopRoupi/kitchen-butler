from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    subscription_status = models.CharField(max_length=50, default='inactive')