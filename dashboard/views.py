from django.views.generic import TemplateView, View
from user.mixins import AdminRequiredMixin


from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from user.models import User
from pages.models import PageVisibility, WhatWeDo
from events.models import Event
from projects.models import Project
from resources.models import Resource
from audit.models import AuditLog
from .forms import (
    PageForm,
    MemberForm,
    WhatWeDoForm,
    EventForm,
    ProjectForm,
    ResourceForm,
)


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


class AuditListView(AdminRequiredMixin, ListView):
    model = AuditLog
    template_name = "dashboard/audit/list.html"
    context_object_name = "audits"
    paginate_by = 10

    def get_queryset(self):
        qs = AuditLog.objects.all().order_by("-timestamp")

        search = self.request.GET.get("search")

        if search:
            qs = qs.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(model_name__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "audit_list"
        return context


class MemberListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "dashboard/member/list.html"
    context_object_name = "members"
    paginate_by = 10

    def get_queryset(self):
        qs = User.objects.all().order_by("-updated_at")

        search = self.request.GET.get("search")
        faculty = self.request.GET.get("faculty")
        batch = self.request.GET.get("batch")

        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        if faculty:
            qs = qs.filter(faculty=faculty)

        if batch:
            qs = qs.filter(batch=batch)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faculty_choices"] = User.FACULTY_CHOICES
        context["batch_choices"] = User.batch_choices()
        context["active_page"] = "members"
        return context


class MemberCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = MemberForm
    template_name = "dashboard/member/form.html"
    success_url = reverse_lazy("dashboard:member_list")

    def form_valid(self, form):
        messages.success(self.request, "Member created successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faculty_choices"] = User.FACULTY_CHOICES
        context["batch_choices"] = User.batch_choices()
        context["page_title"] = "Add Member"
        context["active_page"] = "members"
        return context


class MemberUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = MemberForm
    template_name = "dashboard/member/form.html"
    success_url = reverse_lazy("dashboard:member_list")

    def form_valid(self, form):
        messages.success(self.request, "Member updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faculty_choices"] = User.FACULTY_CHOICES
        context["batch_choices"] = User.batch_choices()
        context["page_title"] = "Edit Member"
        context["active_page"] = "members"
        return context


class MemberDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy("dashboard:member_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Member deleted successfully")
        return super().delete(request, *args, **kwargs)


class MemberActivateView(AdminRequiredMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(User, id=pk)
        member.is_active = True
        member.save()

        messages.success(request, "Member activated successfully")
        next_url = request.POST.get("next") or reverse_lazy("dashboard:member_list")
        return redirect(next_url)


class MemberDeactivateView(AdminRequiredMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(User, id=pk)
        member.is_active = False
        member.save()

        messages.success(request, "Member deactivated successfully")
        next_url = request.POST.get("next") or reverse_lazy("dashboard:member_list")
        return redirect(next_url)


class WhatWeDoListView(AdminRequiredMixin, ListView):
    model = WhatWeDo
    template_name = "dashboard/whatwedo/list.html"
    context_object_name = "what_we_do_list"
    paginate_by = 10

    def get_queryset(self):
        qs = WhatWeDo.objects.all().order_by("-updated_at")
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(caption__icontains=search))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "what_we_do_list"
        return context


class WhatWeDoCreateView(AdminRequiredMixin, CreateView):
    model = WhatWeDo
    form_class = WhatWeDoForm
    template_name = "dashboard/whatwedo/form.html"
    success_url = reverse_lazy("dashboard:what_we_do_list")

    def form_valid(self, form):
        messages.success(self.request, "Activity created successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Activity"
        context["active_page"] = "what_we_do_list"
        return context


class WhatWeDoUpdateView(AdminRequiredMixin, UpdateView):
    model = WhatWeDo
    form_class = WhatWeDoForm
    template_name = "dashboard/whatwedo/form.html"
    success_url = reverse_lazy("dashboard:what_we_do_list")

    def form_valid(self, form):
        messages.success(self.request, "Activity updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit What We Do"
        context["active_page"] = "what_we_do_list"
        return context


class WhatWeDoDeleteView(AdminRequiredMixin, DeleteView):
    model = WhatWeDo
    success_url = reverse_lazy("dashboard:what_we_do_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Activity deleted successfully")
        return super().delete(request, *args, **kwargs)


class EventListView(AdminRequiredMixin, ListView):
    model = Event
    template_name = "dashboard/event/list.html"
    context_object_name = "events"
    paginate_by = 10

    def get_queryset(self):
        qs = Event.objects.all().order_by("-updated_at")
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(caption__icontains=search))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "event_list"
        return context


class EventCreateView(AdminRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "dashboard/event/form.html"
    success_url = reverse_lazy("dashboard:event_list")

    def form_valid(self, form):
        messages.success(self.request, "Event created successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Event"
        context["active_page"] = "event_list"
        return context


class EventUpdateView(AdminRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "dashboard/event/form.html"
    success_url = reverse_lazy("dashboard:event_list")

    def form_valid(self, form):
        messages.success(self.request, "Event updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Event"
        context["active_page"] = "event_list"
        return context


class EventDeleteView(AdminRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy("dashboard:event_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Event deleted successfully")
        return super().delete(request, *args, **kwargs)


class ProjectListView(AdminRequiredMixin, ListView):
    model = Project
    template_name = "dashboard/project/list.html"
    context_object_name = "projects"
    paginate_by = 10

    def get_queryset(self):
        qs = Project.objects.all().order_by("-updated_at")
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(caption__icontains=search))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "project_list"
        return context


class ProjectCreateView(AdminRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "dashboard/project/form.html"
    success_url = reverse_lazy("dashboard:project_list")

    def form_valid(self, form):
        messages.success(self.request, "Project created successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Project"
        context["active_page"] = "project_list"
        context["all_users"] = User.objects.all()
        return context


class ProjectUpdateView(AdminRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "dashboard/project/form.html"
    success_url = reverse_lazy("dashboard:project_list")

    def form_valid(self, form):
        messages.success(self.request, "Project updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Project"
        context["active_page"] = "project_list"
        context["all_users"] = User.objects.all()
        return context


class ProjectDeleteView(AdminRequiredMixin, DeleteView):
    model = Project
    success_url = reverse_lazy("dashboard:project_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Project deleted successfully")
        return super().delete(request, *args, **kwargs)


class ResourceListView(AdminRequiredMixin, ListView):
    model = Resource
    template_name = "dashboard/resource/list.html"
    context_object_name = "resources"
    paginate_by = 10

    def get_queryset(self):
        qs = Resource.objects.all().order_by("-updated_at")
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(caption__icontains=search))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "resource_list"
        return context


class ResourceCreateView(AdminRequiredMixin, CreateView):
    model = Resource
    form_class = ResourceForm
    template_name = "dashboard/resource/form.html"
    success_url = reverse_lazy("dashboard:resource_list")

    def form_valid(self, form):
        messages.success(self.request, "Resource created successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Resource"
        context["active_page"] = "resource_list"
        return context


class ResourceUpdateView(AdminRequiredMixin, UpdateView):
    model = Resource
    form_class = ResourceForm
    template_name = "dashboard/resource/form.html"
    success_url = reverse_lazy("dashboard:resource_list")

    def form_valid(self, form):
        messages.success(self.request, "Resource updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Resource"
        context["active_page"] = "resource_list"
        return context


class ResourceDeleteView(AdminRequiredMixin, DeleteView):
    model = Resource
    success_url = reverse_lazy("dashboard:resource_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Resource deleted successfully")
        return super().delete(request, *args, **kwargs)
