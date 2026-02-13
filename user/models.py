from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import datetime


class User(AbstractUser):
    FACULTY_CHOICES = [
        ("CSIT", "BSc CSIT"),
        ("BCA", "BCA"),
        ("BBS", "BBS"),
        ("BBM", "BBM"),
        ("MBA", "MBA"),
        ("BIT", "BIT"),
    ]

    def batch_choices():
        start_year = 2068
        current_year = datetime.now().year + 57
        return [(str(year), str(year)) for year in range(start_year, current_year + 1)]

    faculty = models.CharField(max_length=10, choices=FACULTY_CHOICES, blank=True)
    batch = models.CharField(max_length=10, choices=batch_choices(), blank=True)
    phone = models.CharField(max_length=15, blank=True)
    interested_topics = models.TextField(help_text="Comma separated topics", blank=True)

    def __str__(self):
        return self.username or (self.first_name + " " + self.last_name)

    @property
    def is_admin_group(self):
        return self.groups.filter(name="Admin").exists()
