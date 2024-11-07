# models.py

from django.db import models
from django.contrib.auth.models import User


class WriterApplication(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    is_approved = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=False)
    applied_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username})"
