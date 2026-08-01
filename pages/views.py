from django.shortcuts import render
from django.utils import timezone
from django.views import View
from pages.models import AboutUs, WhatWeDo
from events.models import Event
from projects.models import Project
from resources.models import Resource


class IndexView(View):
    template = "pages/default/index.html"

    def get(self, request):
        aboutus = AboutUs.objects.first()
        whatwedos = WhatWeDo.objects.filter(display=True).order_by("order")[:10]
        upcomingEvents = Event.objects.order_by("date").filter(
            display=True,
            date__gte=timezone.now(),
        )[:3]
        majorEvents = Event.objects.order_by("-date", "order").filter(
            display=True, is_major=True
        )[:10]
        projects = Project.objects.order_by("order").filter(display=True)[:10]
        resources = Resource.objects.order_by("order").filter(display=True)[:10]

        return render(
            request,
            self.template,
            {
                "aboutus": aboutus,
                "whatwedos": whatwedos,
                "upcomingEvents": upcomingEvents,
                "majorEvents": majorEvents,
                "projects": projects,
                "resources": resources,
            },
        )


class EventsView(View):
    template = "pages/Events.html"

    def get(self, request):
        events = Event.objects.order_by("date").filter(display=True)
        return render(request, self.template, {"events": events})


class ResourceView(View):
    template = "pages/Resources.html"

    def get(self, request):
        resources = Resource.objects.order_by("order").filter(display=True)
        return render(request, self.template, {"resources": resources})
