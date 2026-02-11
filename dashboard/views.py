from django.views.generic import TemplateView, View
from user.mixins import AdminRequiredMixin


from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from user.models import User
from pages.models import PageVisibility
from .forms import PageForm, MemberForm


class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"
    login_url = "/admin/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "dashboard"
        context["total_members"] = User.objects.count()
        return context


class PageView(AdminRequiredMixin, UpdateView):
    model = PageVisibility
    form_class = PageForm
    template_name = "dashboard/page_form.html"
    success_url = reverse_lazy("dashboard:home")

    def get_object(self, queryset=None):
        obj, created = PageVisibility.objects.get_or_create(pk=1)
        return obj

    def form_valid(self, form):
        messages.success(self.request, "Page settings updated successfully")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "page_settings"
        return context


class MemberListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "dashboard/member_list.html"
    context_object_name = "members"
    paginate_by = 10

    def get_queryset(self):
        qs = User.objects.all().order_by("username")

        search = self.request.GET.get("search")
        faculty = self.request.GET.get("faculty")
        batch = self.request.GET.get("batch")

        if search:
            qs = qs.filter(Q(username__icontains=search) | Q(email__icontains=search))

        if faculty:
            qs = qs.filter(faculty=faculty)

        if batch:
            qs = qs.filter(batch=batch)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faculty_choices"] = User.FACULTY_CHOICES
        context["active_page"] = "members"
        return context


class MemberCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = MemberForm
    template_name = "dashboard/member_form.html"
    success_url = reverse_lazy("dashboard:member_list")

    def form_valid(self, form):
        messages.success(self.request, "Member created successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Add Member"
        context["active_page"] = "members"
        return context


class MemberUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = MemberForm
    template_name = "dashboard/member_form.html"
    pk_url_kwarg = "member_id"
    success_url = reverse_lazy("dashboard:member_list")

    def form_valid(self, form):
        messages.success(self.request, "Member updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Member"
        context["active_page"] = "members"
        return context


class MemberDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = "dashboard/member_confirm_delete.html"
    pk_url_kwarg = "member_id"
    success_url = reverse_lazy("dashboard:member_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Member deleted successfully")
        return super().delete(request, *args, **kwargs)


class MemberActivateView(AdminRequiredMixin, View):
    def post(self, request, member_id):
        member = get_object_or_404(User, id=member_id)
        member.is_active = True
        member.save()

        return redirect("dashboard:member_list")


class MemberDeactivateView(AdminRequiredMixin, View):
    def post(self, request, member_id):
        member = get_object_or_404(User, id=member_id)
        member.is_active = False
        member.save()

        return redirect("dashboard:member_list")
