from django.urls import path
from .views import (
    IndexView,
    EventsView,
    ProjectsView,
    ResourceView,
    EventDetailView,
    ProjectDetailView,
    ResourceDetailView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("events/", EventsView.as_view(), name="events"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event_detail"),
    path("projects/", ProjectsView.as_view(), name="projects"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project_detail"),
    path("resource/", ResourceView.as_view(), name="resources"),
    path("resource/<int:pk>/", ResourceDetailView.as_view(), name="resource_detail"),
]
