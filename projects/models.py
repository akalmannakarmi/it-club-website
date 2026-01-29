from django.db import models


# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    technology_stack = models.TextField()
    image = models.ImageField(upload_to="projects_image/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    members_info = models.CharField(max_length=200)

    def __str__(self):
        return self.title
