from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.views.generic import CreateView, TemplateView, ListView
from django.urls import reverse_lazy


from .forms import RegisterForm
from .models import User
from .mixins import AdminRequiredMixin


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "user/register.html"
    success_url = reverse_lazy("user:profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class UserLoginView(LoginView):
    template_name = "user/login.html"


class UserLogoutView(LogoutView):
    pass


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "user/profile.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["user"] = self.request.user
        return ctx


class UsersListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "user/user-list.html"
    context_object_name = "users"
    paginate_by = 10
    ordering = ["-date_joined"]

    def get_queryset(self):
        return User.objects.select_related().prefetch_related("groups")
