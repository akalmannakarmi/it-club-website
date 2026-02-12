from django.shortcuts import render
from django.views import View
from pages.models import PageVisibility,WhatWeDo


class IndexView(View):
    template = "pages/default/index.html"

    def get(self, request):
        visibility = PageVisibility.objects.first()
        whatwedos = WhatWeDo.objects.all()[:10]

        return render(request, self.template, {"visibility": visibility, "whatwedos": whatwedos})


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
