from django.db import models

class PageVisibility(models.Model):
    banner_title = models.TextField("Organization Name", default="Club")
    banner_image = models.ImageField("Banner Image", upload_to="page/banner/",null=True,blank=True)
    banner_desc = models.TextField(null=True,blank=True)

    show_banner = models.BooleanField(default=True)
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
