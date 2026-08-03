from django.db import models
from audit.models import BaseModel
from user.models import User


class Session(BaseModel):
    title = models.TextField("Session Title")
    date = models.DateField("Session Date")
    description = models.TextField("Session Description", null=True, blank=True)

    attendees = models.ManyToManyField(User, related_name="attended_sessions")

    def __str__(self):
        return self.title
