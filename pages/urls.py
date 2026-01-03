from django.urls import path
from .views import IndexView, AnnouncementsView, EventsView, ResourceView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('announcement/', AnnouncementsView.as_view(), name='announcemetn'),
    path('events/', EventsView.as_view(), name='events'),
    path('resource/', ResourceView.as_view(), name='resources'),

]
