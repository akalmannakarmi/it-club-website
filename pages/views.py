from django.shortcuts import render
from django.views import View
from pages.models import PageVisibility


class IndexView(View):
    template = "pages/index.html"

    def get(self, request):
        visibility = PageVisibility.objects.first()

        return render(request, self.template, {"visibility": visibility})


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
