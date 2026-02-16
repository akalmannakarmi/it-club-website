from django.core.cache import cache
from .models import PageSettings


def page_settings(request):
    settings = cache.get("page_settings")

    if not settings:
        settings, created = PageSettings.objects.get_or_create(pk=1)
        cache.set("page_settings", settings, 60 * 60)  # cache 1 hour

    return {"page_settings": settings}
