from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, FormView, View
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import RegisterForm, LoginForm
from .models import User
from .mixins import AdminRequiredMixin


class RegisterView(FormView):
    template_name = "user/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("user:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.set_password(form.cleaned_data["password"])
        user.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faculty_choices"] = User.FACULTY_CHOICES
        context["batch_choices"] = User.batch_choices()

        return context


class LoginView(FormView):
    template_name = "user/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(self.request, "Invalid email or password")
            return self.form_invalid(form)

        user = authenticate(self.request, username=user_obj.username, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)

        messages.error(self.request, "Invalid email or password")
        return self.form_invalid(form)


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("/")


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
