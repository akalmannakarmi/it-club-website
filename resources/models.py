from django.db import models
from django.core.validators import FileExtensionValidator


ALLOWED_EXTENSIONS = FileExtensionValidator(
    allowed_extensions=["pdf", "doc", "docx", "txt", "ppt", "pptx"]
)


class Resource(models.Model):
    title = models.CharField("Resource Title", max_length=200)
    caption = models.TextField("Resource Caption", null=True, blank=True)
    image = models.ImageField(
        "Resource Image", upload_to="resources/", null=True, blank=True
    )
    description = models.TextField("Resource Description", blank=True)
    url = models.URLField("Resource Video URL", blank=True, null=True)
    file = models.FileField(
        "Resource attached file",
        upload_to="resources/file/",
        blank=True,
        null=True,
        validators=[ALLOWED_EXTENSIONS],
    )

    def __str__(self):
        return self.title
