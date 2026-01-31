from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    FACULTY_CHOICES = [
        ("CSIT", "BSc CSIT"),
        ("BCA", "BCA"),
        ("BBS", "BBS"),
        ("BBM", "BBM"),
        ("MBA", "MBA"),
        ("BIT", "BIT"),
    ]

    faculty = models.CharField(max_length=10, choices=FACULTY_CHOICES, blank=True)
    batch = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    interested_topics = models.TextField(help_text="Comma separated topics", blank=True)

    def __str__(self):
        return self.username

    @property
    def is_admin_group(self):
        return self.groups.filter(name="Admin").exists()
