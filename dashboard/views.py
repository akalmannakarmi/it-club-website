from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    View,
)
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import timedelta, datetime
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.utils.http import url_has_allowed_host_and_scheme


from user.utils.email import send_html_email
from user.mixins import (
    AdminRequiredMixin,
    MemberRequiredMixin,
    AdminOrOwnerRequiredMixin,
)
from user.models import User
from pages.models import PageSettings, AboutUs, WhatWeDo
from events.models import Event
from projects.models import Project
from resources.models import Resource
from audit.models import AuditLog
from attendance.models import Session
from .forms import (
    PageForm,
    AboutUsForm,
    MemberForm,
    WhatWeDoForm,
    EventForm,
    ProjectForm,
    ResourceForm,
    SessionForm,
)


def _safe_next(request, fallback):
    next_url = request.POST.get("next")
    if next_url and not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        next_url = None
    return next_url or fallback


class DashboardView(MemberRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "dashboard"
        context["total_members"] = User.objects.count()
        context["total_events"] = Event.objects.count()
        context["total_projects"] = Project.objects.count()
        context["total_resources"] = Resource.objects.count()

        last_three_sessions = list(Session.objects.order_by("-date")[:3])
        active_members = (
            User.objects.filter(attended_sessions__in=last_three_sessions)
            .distinct()
            .count()
        )

        now = datetime.now()
        last_30_days = now - timedelta(days=30)
        recent_sessions = Session.objects.filter(date__gte=last_30_days)

        attendees_this_month = (
            User.objects.filter(attended_sessions__in=recent_sessions)
            .distinct()
            .count()
        )

        previous_30_days = now - timedelta(days=60)
        previous_sessions = Session.objects.filter(
            date__gte=previous_30_days, date__lt=last_30_days
        )

        attendees_previous = (
            User.objects.filter(attended_sessions__in=previous_sessions)
            .distinct()
            .count()
        )

        if attendees_previous > 0:
            attendees_change = round(
                ((attendees_this_month - attendees_previous) / attendees_previous) * 100
            )
        else:
            attendees_change = 100 if attendees_this_month > 0 else 0

        context["active_members"] = active_members
        context["attendees_this_month"] = attendees_this_month
        context["attendees_change"] = attendees_change

        return context


class ActivityView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        days = int(request.GET.get("days", 30))
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # Prepare date labels
        date_labels = [
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(days + 1)
        ]

        # Count sessions per day
        session_counts = []
        attendee_counts = []
        for d in date_labels:
            day = datetime.strptime(d, "%Y-%m-%d").date()
            sessions = Session.objects.filter(date=day)
            session_counts.append(sessions.count())
            attendee_counts.append(sum(s.attendees.count() for s in sessions))

        # Count events
        event_counts = [Event.objects.filter(date__date=d).count() for d in date_labels]

        # Count projects
        project_counts = [
            Project.objects.filter(created_at__date=d).count() for d in date_labels
        ]

        # Count resources
        resource_counts = [
            Resource.objects.filter(created_at__date=d).count() for d in date_labels
        ]

        # Count new users
        user_counts = [
            User.objects.filter(created_at__date=d).count() for d in date_labels
        ]

        return JsonResponse(
            {
                "labels": date_labels,
                "sessions": session_counts,
                "attendees": attendee_counts,
                "events": event_counts,
                "projects": project_counts,
                "resources": resource_counts,
                "users": user_counts,
            }
        )


class PageView(AdminRequiredMixin, UpdateView):
    model = PageSettings
    form_class = PageForm
    template_name = "dashboard/page_form.html"
    success_url = reverse_lazy("dashboard:home")

    def get_object(self, queryset=None):
        obj, created = PageSettings.objects.get_or_create(pk=1)
        return obj

    def form_valid(self, form):
        messages.success(self.request, "Page settings updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "page_settings"
        return context


class AboutUsView(AdminRequiredMixin, UpdateView):
    model = AboutUs
    form_class = AboutUsForm
    template_name = "dashboard/about_form.html"
    success_url = reverse_lazy("dashboard:home")

    def get_object(self, queryset=None):
        obj, created = AboutUs.objects.get_or_create(pk=1)
        return obj

    def form_valid(self, form):
        messages.success(self.request, "About Us updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "about_us"
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
        response = super().form_valid(form)

        member_group, _ = Group.objects.get_or_create(name="Member")
        self.object.groups.add(member_group)

        try:
            send_html_email(
                subject="Your account has been created",
                template="user/emails/member_invited.html",
                to_email=self.object.email,
                context={"user": self.object},
                request=self.request,
            )
        except Exception as e:
            print(f"Failed to send invite email for {self.object}: {e}")

        messages.success(
            self.request,
            "Member created. An invite email with password set-up instructions was sent.",
        )
        return response

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

        try:
            send_html_email(
                subject="Your account has been activated",
                template="user/emails/account_activated.html",
                to_email=member.email,
                context={"user": member},
                request=request,
            )
        except Exception as e:
            print(f"Failed to send account activation email: {e}")

        messages.success(request, "Member activated successfully")
        return redirect(_safe_next(request, reverse_lazy("dashboard:member_list")))


class MemberDeactivateView(AdminRequiredMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(User, id=pk)
        member.is_active = False
        member.save()

        try:
            send_html_email(
                subject="Your account has been deactivated",
                template="user/emails/account_deactivated.html",
                to_email=member.email,
                context={"user": member},
                request=request,
            )
        except Exception as e:
            print(f"Failed to send account deactivation email: {e}")

        messages.success(request, "Member deactivated successfully")
        return redirect(_safe_next(request, reverse_lazy("dashboard:member_list")))


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


class EventListView(MemberRequiredMixin, ListView):
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


class EventDetailView(MemberRequiredMixin, DetailView):
    model = Event
    template_name = "dashboard/event/detail.html"
    context_object_name = "event"

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


class MyProjectListView(MemberRequiredMixin, ListView):
    model = Project
    template_name = "dashboard/project/list.html"
    context_object_name = "projects"
    paginate_by = 10

    def get_queryset(self):
        qs = Project.objects.filter(
            Q(supervisor=self.request.user) | Q(members=self.request.user)
        ).order_by("-updated_at")
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(caption__icontains=search))

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "project_list"
        return context


class ProjectDetailView(AdminOrOwnerRequiredMixin, DetailView):
    model = Project
    template_name = "dashboard/project/detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "project_list"

        tech_stack = self.object.technology_stack
        if tech_stack:
            context["tech_list"] = [t.strip() for t in tech_stack.split(",")]
        else:
            context["tech_list"] = []

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


class ResourceListView(MemberRequiredMixin, ListView):
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


class ResourceDetailView(MemberRequiredMixin, DetailView):
    model = Resource
    template_name = "dashboard/resource/detail.html"
    context_object_name = "resource"

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


class SessionListView(MemberRequiredMixin, ListView):
    model = Session
    template_name = "dashboard/session/list.html"
    context_object_name = "sessions"
    paginate_by = 10

    def get_queryset(self):
        qs = Session.objects.all().order_by("-updated_at")
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "session_list"
        return context


class SessionDetailView(MemberRequiredMixin, DetailView):
    model = Session
    template_name = "dashboard/session/detail.html"
    context_object_name = "session"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "session_list"
        return context


class SessionCreateView(AdminRequiredMixin, CreateView):
    model = Session
    form_class = SessionForm
    template_name = "dashboard/session/form.html"
    success_url = reverse_lazy("dashboard:session_list")

    def form_valid(self, form):
        messages.success(self.request, "Session created successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Session"
        context["active_page"] = "session_list"
        context["members"] = User.objects.filter(is_active=True).order_by("first_name")
        return context


class SessionUpdateView(AdminRequiredMixin, UpdateView):
    model = Session
    form_class = SessionForm
    template_name = "dashboard/session/form.html"
    success_url = reverse_lazy("dashboard:session_list")

    def form_valid(self, form):
        messages.success(self.request, "Session updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Session"
        context["active_page"] = "session_list"
        context["members"] = User.objects.filter(is_active=True).order_by("first_name")
        return context


class SessionDeleteView(AdminRequiredMixin, DeleteView):
    model = Session
    success_url = reverse_lazy("dashboard:session_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Session deleted successfully")
        return super().delete(request, *args, **kwargs)


class AttendanceListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "dashboard/attendance/list.html"
    context_object_name = "members"
    paginate_by = 10

    def get_queryset(self):
        qs = (
            User.objects.filter(is_active=True)
            .annotate(attended_count=Count("attended_sessions"))
            .order_by("first_name")
        )

        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_sessions = Session.objects.count()
        context["total_sessions"] = total_sessions
        context["active_page"] = "attendance_list"

        for member in context["members"]:
            if total_sessions > 0:
                member.attendance_percent = round(
                    (member.attended_count / total_sessions) * 100
                )
            else:
                member.attendance_percent = 0

        return context


class AttendanceDetailView(AdminRequiredMixin, ListView):
    model = Session
    template_name = "dashboard/attendance/detail.html"
    context_object_name = "sessions"
    paginate_by = 10

    def get_queryset(self):
        self.member = get_object_or_404(User, id=self.kwargs["pk"])

        return Session.objects.all().order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        attended_ids = set(self.member.attended_sessions.values_list("id", flat=True))

        for session in context["sessions"]:
            session.attended = session.id in attended_ids

        context["member"] = self.member
        context["active_page"] = "attendance_list"

        return context


class MyAttendanceDetailView(MemberRequiredMixin, ListView):
    model = Session
    template_name = "dashboard/attendance/detail.html"
    context_object_name = "sessions"
    paginate_by = 10

    def get_queryset(self):
        self.member = self.request.user

        return Session.objects.all().order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        attended_ids = set(self.member.attended_sessions.values_list("id", flat=True))

        for session in context["sessions"]:
            session.attended = session.id in attended_ids

        context["member"] = self.member
        context["active_page"] = "attendance_list"

        return context
