from django.shortcuts import render
from django.utils.timezone import datetime
from django.views import View
from pages.models import PageVisibility,WhatWeDo
from events.models import Event
from projects.models import Project
from resources.models import Resource

class IndexView(View):
    template = "pages/default/index.html"

    def get(self, request):
        visibility = PageVisibility.objects.first()
        whatwedos = WhatWeDo.objects.all()[:10]
        upcomingEvents = Event.objects.order_by("date").filter(date__gte=datetime.now().date())[:3]
        majorEvents = Event.objects.order_by("-date").filter(is_major=True)[:10]
        projects = Project.objects.order_by("-id").all()[:10]
        resources = Resource.objects.order_by("-id").all()[:10]

        return render(request, self.template, {"visibility": visibility, "whatwedos": whatwedos, "upcomingEvents":upcomingEvents, "majorEvents":majorEvents, "projects":projects, "resources":resources})


class AnnouncementsView(View):
    template = "pages/Announcements.html"

    def get(self, request):
        return render(request, self.template)


class EventsView(View):
    template = "pages/Events.html"

    def get(self, request):
        return render(request, self.template)


class ResourceView(View):
    template = "pages/Resources.html"

    def get(self, request):
        return render(request, self.template)
