from django.db import models
from audit.models import BaseModel
from user.models import User


# Create your models here.
class Session(BaseModel):
    title = models.TextField("Session Title")
    date = models.DateField("Session Date")
    description = models.TextField("Session Description", null=True, blank=True)

    attendees = models.ManyToManyField(User, related_name="attended_sessions")
