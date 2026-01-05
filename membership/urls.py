from django.contrib import admin
from django.urls import path
from .views import  Delete_user



urlpatterns = [
    path('admin/', admin.site.urls),
    path('delete_user/<int:pid>/', Delete_user, name='delete_user'),
    
    ]