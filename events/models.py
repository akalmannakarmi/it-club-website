from django.db import models
from audit.models import BaseModel


class Event(BaseModel):
    title = models.TextField("Event Title")
    caption = models.TextField("Event Caption", null=True, blank=True)
    image = models.ImageField("Event Image", upload_to="events/", null=True, blank=True)
    date = models.DateTimeField("Event Date")
    is_major = models.BooleanField("Is Major Event", default=False)
    description = models.TextField("Event Description", null=True, blank=True)
