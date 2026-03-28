from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout, views as auth_views
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, FormView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.conf import settings
from user.utils.email import send_html_email

from pages.models import AboutUs
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

        try:
            send_html_email(
                subject="Registration received – awaiting approval",
                template="user/emails/register_received.html",
                to_email=user.email,
                context={"user": user},
                request=self.request,
            )
            send_html_email(
                subject="New member registration",
                template="user/emails/admin_new_registration.html",
                to_email=settings.EMAIL_HOST_USER,
                context={"user": user},
                request=self.request,
            )
        except Exception as e:
            print(f"Failed to send email for {user}'s registration: {e}")

        messages.success(
            self.request,
            "Registration submitted. Please wait for admin approval."
        )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faculty_choices"] = User.FACULTY_CHOICES
        context["batch_choices"] = User.batch_choices()
        context["aboutus"] = AboutUs.objects.first()

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

        user = authenticate(self.request, email=user_obj.email, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)

        messages.error(self.request, "Invalid email or password")
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["aboutus"] = AboutUs.objects.first()
        return context


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



class PasswordResetView(auth_views.PasswordResetView):
    template_name = "user/password_reset.html"

    email_template_name = "user/emails/password_reset_email.txt"
    html_email_template_name = "user/emails/password_reset_email.html"

    success_url = reverse_lazy("user:password_reset_done")

    def get_subject(self):
        return "Reset your Academia IT Club password"

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = self.get_subject()

        super().send_mail(
            subject,
            email_template_name,
            context,
            from_email,
            to_email,
            html_email_template_name,
        )


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "user/password_reset_done.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "user/password_reset_confirm.html"
    success_url = reverse_lazy("user:password_reset_complete")


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "user/password_reset_complete.html"
