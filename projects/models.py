from django.db import models
from user.models import User


class Project(models.Model):
    title = models.CharField("Project Title", max_length=200)
    caption = models.TextField("Project Caption", null=True, blank=True)
    description = models.TextField("Project Description", null=True, blank=True)
    technology_stack = models.TextField(
        "Project Technology Used", null=True, blank=True
    )
    image = models.ImageField(
        "Project Image", upload_to="projects/", blank=True, null=True
    )
    link = models.URLField("Project Live URL", blank=True, null=True)
    repo_link = models.URLField("Project Repository URL", blank=True, null=True)
    supervisor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="supervised_projects",
    )
    members = models.ManyToManyField(User, related_name="projects")

    def __str__(self):
        return self.title
