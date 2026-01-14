from django.db import models

# Create your models here.

class PageVisibility(models.Model):
    show_home = models.BooleanField(default=True)
    show_resource = models.BooleanField(default=True)
    show_event = models.BooleanField(default=True)
    show_announcement = models.BooleanField(default=True)

    def __str__(self):
        return "Page Visibility Settings"