from django.db import models
from django.utils import timezone


class Member(models.Model):
    FACULTY_CHOICES = [
        ('CSIT', 'BSc CSIT'),
        ('BCA', 'BCA'),
        ('BBS', 'BBS'),
        ('BBM', 'BBM'),
        ('MBA', 'MBA'),
        ('BIT', 'BIT'),
         ]

    name = models.CharField(max_length=150,default="")
    semester=models.CharField()
    phone = models.CharField(max_length=15)
    faculty = models.CharField(max_length=10, choices=FACULTY_CHOICES)
    interested_topics = models.TextField(help_text="Comma separated topics")
    
    
    is_active = models.BooleanField(default=True)
    is_deactive = models.BooleanField(default=False)

    def __str__(self):
     return self.name

