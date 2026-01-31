from django.db import models

# Create your models here.


class PageVisibility(models.Model):
    show_hero = models.BooleanField(default=True)
    show_about = models.BooleanField(default=True)
    show_whatwedo = models.BooleanField(default=True)
    show_upcoming = models.BooleanField(default=True)
    show_projects = models.BooleanField(default=True)
    show_resources = models.BooleanField(default=True)
    show_events = models.BooleanField(default=True)
    show_footer = models.BooleanField(default=True)

    def __str__(self):
        return "Page Visibility Settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # force singleton
        super().save(*args, **kwargs)
