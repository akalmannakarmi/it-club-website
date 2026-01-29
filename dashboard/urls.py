from django.urls import path
from . import views 

from .views import (
    MemberListView,
    MemberCreateView,
    MemberUpdateView,
    MemberDeleteView,
    MemberActivateView,
    MemberDeactivateView,
)

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='home'),
    
    
    path('members/', MemberListView.as_view(), name='member_list'),
    path('members/create/', MemberCreateView.as_view(), name='member_create'),
    path('members/edit/<int:member_id>/', MemberUpdateView.as_view(), name='member_edit'),
    path('members/delete/<int:member_id>/', MemberDeleteView.as_view(), name='member_delete'),
    path('members/activate/<int:member_id>/', MemberActivateView.as_view(), name='member_activate'),
    path('members/deactivate/<int:member_id>/', MemberDeactivateView.as_view(), name='member_deactivate'),
]

