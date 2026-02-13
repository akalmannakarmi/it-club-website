from django.db import models


class Event(models.Model):
    title = models.TextField("Event Title", unique=True)
    caption = models.TextField("Event Caption", null=True, blank=True)
    image = models.ImageField("Event Image", upload_to="events/", null=True, blank=True)
    date = models.DateTimeField("Event Date")
    is_major = models.BooleanField("Is Major Event", default=False)
    description = models.TextField("Event Description", null=True, blank=True)
