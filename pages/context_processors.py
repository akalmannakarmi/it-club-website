from django.core.cache import cache
from .models import PageSettings


def page_settings(request):
    settings = cache.get("page_settings")

    if not settings:
        settings = PageSettings.objects.filter(pk=1).first()
        if not settings:
            settings = PageSettings()
            settings.save(no_audit=True)
        cache.set("page_settings", settings, 60 * 60)  # cache 1 hour

    return {"page_settings": settings}
