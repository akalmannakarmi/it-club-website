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
from django.db.models.functions import TruncDate
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
from .mixins import DashboardContextMixin, SearchableListMixin


def _safe_next(request, fallback):
    next_url = request.POST.get("next")
    if next_url and not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        next_url = None
    return next_url or fallback


class DashboardView(MemberRequiredMixin, DashboardContextMixin, TemplateView):
    template_name = "dashboard/dashboard.html"
    active_page = "dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        try:
            days = int(request.GET.get("days", 30))
        except ValueError:
            days = 30
        days = min(max(days, 1), 366)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        date_labels = [
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(days + 1)
        ]

        def counts_by_day(queryset, field):
            rows = (
                queryset.filter(**{f"{field}__gte": start_date})
                .annotate(day=TruncDate(field))
                .values("day")
                .annotate(count=Count("id"))
            )
            return {row["day"].isoformat(): row["count"] for row in rows}

        session_map = counts_by_day(Session.objects.all(), "date")
        event_map = counts_by_day(Event.objects.all(), "date")
        project_map = counts_by_day(Project.objects.all(), "created_at")
        resource_map = counts_by_day(Resource.objects.all(), "created_at")
        user_map = counts_by_day(User.objects.all(), "created_at")

        attendee_map = {
            row["day"].isoformat(): row["count"]
            for row in Session.attendees.through.objects.filter(
                session__date__gte=start_date
            )
            .annotate(day=TruncDate("session__date"))
            .values("day")
            .annotate(count=Count("user_id", distinct=True))
        }

        return JsonResponse(
            {
                "labels": date_labels,
                "sessions": [session_map.get(d, 0) for d in date_labels],
                "attendees": [attendee_map.get(d, 0) for d in date_labels],
                "events": [event_map.get(d, 0) for d in date_labels],
                "projects": [project_map.get(d, 0) for d in date_labels],
                "resources": [resource_map.get(d, 0) for d in date_labels],
                "users": [user_map.get(d, 0) for d in date_labels],
            }
        )


class PageView(AdminRequiredMixin, DashboardContextMixin, UpdateView):
    model = PageSettings
    form_class = PageForm
    template_name = "dashboard/page_form.html"
    success_url = reverse_lazy("dashboard:home")
    active_page = "page_settings"
    success_message = "Page settings updated successfully"

    def get_object(self, queryset=None):
        obj, created = PageSettings.objects.get_or_create(pk=1)
        return obj


class AboutUsView(AdminRequiredMixin, DashboardContextMixin, UpdateView):
    model = AboutUs
    form_class = AboutUsForm
    template_name = "dashboard/about_form.html"
    success_url = reverse_lazy("dashboard:home")
    active_page = "about_us"
    success_message = "About Us updated successfully"

    def get_object(self, queryset=None):
        obj, created = AboutUs.objects.get_or_create(pk=1)
        return obj


class AuditListView(AdminRequiredMixin, DashboardContextMixin, ListView):
    model = AuditLog
    template_name = "dashboard/audit/list.html"
    context_object_name = "audits"
    paginate_by = 10
    active_page = "audit_list"

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


class MemberListView(AdminRequiredMixin, DashboardContextMixin, ListView):
    model = User
    template_name = "dashboard/member/list.html"
    context_object_name = "members"
    paginate_by = 10
    active_page = "members"

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
        return context


class MemberCreateView(AdminRequiredMixin, DashboardContextMixin, CreateView):
    model = User
    form_class = MemberForm
    template_name = "dashboard/member/form.html"
    success_url = reverse_lazy("dashboard:member_list")
    active_page = "members"
    page_title = "Add Member"

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
        return context


class MemberUpdateView(AdminRequiredMixin, DashboardContextMixin, UpdateView):
    model = User
    form_class = MemberForm
    template_name = "dashboard/member/form.html"
    success_url = reverse_lazy("dashboard:member_list")
    active_page = "members"
    page_title = "Edit Member"
    success_message = "Member updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faculty_choices"] = User.FACULTY_CHOICES
        context["batch_choices"] = User.batch_choices()
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


class WhatWeDoListView(
    AdminRequiredMixin, SearchableListMixin, DashboardContextMixin, ListView
):
    model = WhatWeDo
    template_name = "dashboard/whatwedo/list.html"
    context_object_name = "what_we_do_list"
    paginate_by = 10
    active_page = "what_we_do_list"
    search_fields = ("title", "caption")


class WhatWeDoCreateView(AdminRequiredMixin, DashboardContextMixin, CreateView):
    model = WhatWeDo
    form_class = WhatWeDoForm
    template_name = "dashboard/whatwedo/form.html"
    success_url = reverse_lazy("dashboard:what_we_do_list")
    active_page = "what_we_do_list"
    page_title = "Create Activity"
    success_message = "Activity created successfully"


class WhatWeDoUpdateView(AdminRequiredMixin, DashboardContextMixin, UpdateView):
    model = WhatWeDo
    form_class = WhatWeDoForm
    template_name = "dashboard/whatwedo/form.html"
    success_url = reverse_lazy("dashboard:what_we_do_list")
    active_page = "what_we_do_list"
    page_title = "Edit What We Do"
    success_message = "Activity updated successfully"


class WhatWeDoDeleteView(AdminRequiredMixin, DeleteView):
    model = WhatWeDo
    success_url = reverse_lazy("dashboard:what_we_do_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Activity deleted successfully")
        return super().delete(request, *args, **kwargs)


class EventListView(
    MemberRequiredMixin, SearchableListMixin, DashboardContextMixin, ListView
):
    model = Event
    template_name = "dashboard/event/list.html"
    context_object_name = "events"
    paginate_by = 10
    active_page = "event_list"
    search_fields = ("title", "caption")


class EventDetailView(MemberRequiredMixin, DashboardContextMixin, DetailView):
    model = Event
    template_name = "dashboard/event/detail.html"
    context_object_name = "event"
    active_page = "event_list"


class EventCreateView(AdminRequiredMixin, DashboardContextMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "dashboard/event/form.html"
    success_url = reverse_lazy("dashboard:event_list")
    active_page = "event_list"
    page_title = "Create Event"
    success_message = "Event created successfully"


class EventUpdateView(AdminRequiredMixin, DashboardContextMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "dashboard/event/form.html"
    success_url = reverse_lazy("dashboard:event_list")
    active_page = "event_list"
    page_title = "Edit Event"
    success_message = "Event updated successfully"


class EventDeleteView(AdminRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy("dashboard:event_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Event deleted successfully")
        return super().delete(request, *args, **kwargs)


class ProjectListView(
    AdminRequiredMixin, SearchableListMixin, DashboardContextMixin, ListView
):
    model = Project
    template_name = "dashboard/project/list.html"
    context_object_name = "projects"
    paginate_by = 10
    active_page = "project_list"
    search_fields = ("title", "caption")


class MyProjectListView(MemberRequiredMixin, DashboardContextMixin, ListView):
    model = Project
    template_name = "dashboard/project/list.html"
    context_object_name = "projects"
    paginate_by = 10
    active_page = "project_list"

    def get_queryset(self):
        qs = Project.objects.filter(
            Q(supervisor=self.request.user) | Q(members=self.request.user)
        ).order_by("-updated_at")
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(caption__icontains=search))

        return qs.distinct()


class ProjectDetailView(AdminOrOwnerRequiredMixin, DashboardContextMixin, DetailView):
    model = Project
    template_name = "dashboard/project/detail.html"
    context_object_name = "project"
    active_page = "project_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tech_stack = self.object.technology_stack
        if tech_stack:
            context["tech_list"] = [t.strip() for t in tech_stack.split(",")]
        else:
            context["tech_list"] = []

        return context


class ProjectCreateView(AdminRequiredMixin, DashboardContextMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "dashboard/project/form.html"
    success_url = reverse_lazy("dashboard:project_list")
    active_page = "project_list"
    page_title = "Create Project"
    success_message = "Project created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_users"] = User.objects.all()
        return context


class ProjectUpdateView(AdminRequiredMixin, DashboardContextMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "dashboard/project/form.html"
    success_url = reverse_lazy("dashboard:project_list")
    active_page = "project_list"
    page_title = "Edit Project"
    success_message = "Project updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_users"] = User.objects.all()
        return context


class ProjectDeleteView(AdminRequiredMixin, DeleteView):
    model = Project
    success_url = reverse_lazy("dashboard:project_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Project deleted successfully")
        return super().delete(request, *args, **kwargs)


class ResourceListView(
    MemberRequiredMixin, SearchableListMixin, DashboardContextMixin, ListView
):
    model = Resource
    template_name = "dashboard/resource/list.html"
    context_object_name = "resources"
    paginate_by = 10
    active_page = "resource_list"
    search_fields = ("title", "caption")


class ResourceDetailView(MemberRequiredMixin, DashboardContextMixin, DetailView):
    model = Resource
    template_name = "dashboard/resource/detail.html"
    context_object_name = "resource"
    active_page = "resource_list"


class ResourceCreateView(AdminRequiredMixin, DashboardContextMixin, CreateView):
    model = Resource
    form_class = ResourceForm
    template_name = "dashboard/resource/form.html"
    success_url = reverse_lazy("dashboard:resource_list")
    active_page = "resource_list"
    page_title = "Create Resource"
    success_message = "Resource created successfully"


class ResourceUpdateView(AdminRequiredMixin, DashboardContextMixin, UpdateView):
    model = Resource
    form_class = ResourceForm
    template_name = "dashboard/resource/form.html"
    success_url = reverse_lazy("dashboard:resource_list")
    active_page = "resource_list"
    page_title = "Edit Resource"
    success_message = "Resource updated successfully"


class ResourceDeleteView(AdminRequiredMixin, DeleteView):
    model = Resource
    success_url = reverse_lazy("dashboard:resource_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Resource deleted successfully")
        return super().delete(request, *args, **kwargs)


class SessionListView(
    MemberRequiredMixin, SearchableListMixin, DashboardContextMixin, ListView
):
    model = Session
    template_name = "dashboard/session/list.html"
    context_object_name = "sessions"
    paginate_by = 10
    active_page = "session_list"
    search_fields = ("title",)


class SessionDetailView(MemberRequiredMixin, DashboardContextMixin, DetailView):
    model = Session
    template_name = "dashboard/session/detail.html"
    context_object_name = "session"
    active_page = "session_list"


class SessionCreateView(AdminRequiredMixin, DashboardContextMixin, CreateView):
    model = Session
    form_class = SessionForm
    template_name = "dashboard/session/form.html"
    success_url = reverse_lazy("dashboard:session_list")
    active_page = "session_list"
    page_title = "Create Session"
    success_message = "Session created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["members"] = User.objects.filter(is_active=True).order_by("first_name")
        return context


class SessionUpdateView(AdminRequiredMixin, DashboardContextMixin, UpdateView):
    model = Session
    form_class = SessionForm
    template_name = "dashboard/session/form.html"
    success_url = reverse_lazy("dashboard:session_list")
    active_page = "session_list"
    page_title = "Edit Session"
    success_message = "Session updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["members"] = User.objects.filter(is_active=True).order_by("first_name")
        return context


class SessionDeleteView(AdminRequiredMixin, DeleteView):
    model = Session
    success_url = reverse_lazy("dashboard:session_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Session deleted successfully")
        return super().delete(request, *args, **kwargs)


class AttendanceListView(AdminRequiredMixin, DashboardContextMixin, ListView):
    model = User
    template_name = "dashboard/attendance/list.html"
    context_object_name = "members"
    paginate_by = 10
    active_page = "attendance_list"

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

        for member in context["members"]:
            if total_sessions > 0:
                member.attendance_percent = round(
                    (member.attended_count / total_sessions) * 100
                )
            else:
                member.attendance_percent = 0

        return context


class AttendanceDetailView(AdminRequiredMixin, DashboardContextMixin, ListView):
    model = Session
    template_name = "dashboard/attendance/detail.html"
    context_object_name = "sessions"
    paginate_by = 10
    active_page = "attendance_list"

    def get_queryset(self):
        self.member = get_object_or_404(User, id=self.kwargs["pk"])

        return Session.objects.all().order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        attended_ids = set(self.member.attended_sessions.values_list("id", flat=True))

        for session in context["sessions"]:
            session.attended = session.id in attended_ids

        context["member"] = self.member

        return context


class MyAttendanceDetailView(MemberRequiredMixin, AttendanceDetailView):
    def get_queryset(self):
        self.member = self.request.user

        return Session.objects.all().order_by("-date")
