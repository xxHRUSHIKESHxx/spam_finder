# api/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)

class Contact(models.Model):
    user = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    is_spam = models.BooleanField(default=False)

    def spam_likelihood(self):
        total_reports = Contact.objects.filter(phone_number=self.phone_number).count()
        spam_reports = Contact.objects.filter(phone_number=self.phone_number, is_spam=True).count()
        if total_reports == 0:
            return 0
        return (spam_reports / total_reports) * 100
