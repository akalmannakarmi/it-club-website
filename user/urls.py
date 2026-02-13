from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    RegisterView,
    ProfileView,
    UsersListView,
)

app_name = "user"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("users/", UsersListView.as_view(), name="user_list"),
]
