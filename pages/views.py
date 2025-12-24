from django.shortcuts import render
from django.views import View

# Create your views here.

class indexView(View):
    template = "pages/index.html"

    def get(self, request):
        return render(request, self.template)
    

class announcementsView(View):
    template = "pages/Announcements.html"

    def get(self, request):
        return render(request, self.template)


class eventsView(View):
    template = "pages/Events.html"

    def get(self, request):
        return render(request, self.template)
    

class resourceView(View):
    template = "pages/Resources.html"

    def get(self, request):
        return render(request, self.template)