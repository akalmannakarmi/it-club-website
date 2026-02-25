from django.db import models
from audit.models import BaseModel
from django.core.cache import cache


class PageSettings(BaseModel):
    org_name = models.TextField("Organization Name", default="Club")
    page_icon = models.ImageField(
        "Page Icon", upload_to="pages/icon/", null=True, blank=True
    )

    show_banner = models.BooleanField(default=True)
    show_about = models.BooleanField(default=True)
    show_whatwedo = models.BooleanField(default=True)
    show_upcoming = models.BooleanField(default=True)
    show_projects = models.BooleanField(default=True)
    show_resources = models.BooleanField(default=True)
    show_events = models.BooleanField(default=True)
    show_footer = models.BooleanField(default=True)

    def __str__(self):
        return "Page Settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # force singleton
        super().save(*args, **kwargs)
        cache.delete("page_settings")


class WhatWeDo(BaseModel):
    title = models.TextField("Activity Title")
    caption = models.TextField("Activity Caption", null=True, blank=True)
    image = models.ImageField(upload_to="pages/activity", null=True, blank=True)
    description = models.TextField("Activity Description", null=True, blank=True)


class AboutUs(BaseModel):
    caption = models.TextField("Caption")
    main_image = models.ImageField(
        "Main Image", upload_to="pages/about/main/", null=True, blank=True
    )
    description = models.TextField("Description", null=True, blank=True)
    location = models.TextField("Location", null=True, blank=True)
    contact_email = models.EmailField("Contact Email", null=True, blank=True)
    contact_phone = models.TextField("Contact Phone Nos", null=True, blank=True)
    contact_facebook = models.TextField("Contact Facebook page", null=True, blank=True)
    contact_twitter = models.TextField("Contact Twitter page", null=True, blank=True)
    contact_reddit = models.TextField("Contact Reddit page", null=True, blank=True)

    def __str__(self):
        return "About Us"

    def save(self, *args, **kwargs):
        self.pk = 1  # force singleton
        super().save(*args, **kwargs)
