from django.contrib import admin
from django.urls import path
from .views import indexView,announcementsView,eventsView,resourceView
urlpatterns = [
    path('', indexView.as_view(), name='index'),
    path('Announcement/', announcementsView.as_view(), name='announcemetn'),
    path('Events/',eventsView.as_view(), name='events'),
    path('Resource/',resourceView.as_view(), name='resources'),
]
