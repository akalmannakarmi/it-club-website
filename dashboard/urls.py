from django.urls import path

from .views import (
    DashboardView,
    ActivityView,
    PageView,
    AboutUsView,
    MemberListView,
    MemberCreateView,
    MemberUpdateView,
    MemberDeleteView,
    MemberActivateView,
    MemberDeactivateView,
    WhatWeDoListView,
    WhatWeDoCreateView,
    WhatWeDoUpdateView,
    WhatWeDoDeleteView,
    EventListView,
    EventDetailView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    ProjectListView,
    MyProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    ResourceListView,
    ResourceDetailView,
    ResourceCreateView,
    ResourceUpdateView,
    ResourceDeleteView,
    AuditListView,
    SessionListView,
    SessionDetailView,
    SessionCreateView,
    SessionUpdateView,
    SessionDeleteView,
    AttendanceListView,
    AttendanceDetailView,
    MyAttendanceDetailView,
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("activity-data/", ActivityView.as_view(), name="activity_data"),
    path("page/", PageView.as_view(), name="page_settings"),
    path("about-us/", AboutUsView.as_view(), name="about_us"),
    path("audit/", AuditListView.as_view(), name="audit_list"),
    path("members/", MemberListView.as_view(), name="member_list"),
    path("members/create/", MemberCreateView.as_view(), name="member_create"),
    path("members/edit/<int:pk>/", MemberUpdateView.as_view(), name="member_edit"),
    path("members/delete/<int:pk>/", MemberDeleteView.as_view(), name="member_delete"),
    path(
        "members/activate/<int:pk>/",
        MemberActivateView.as_view(),
        name="member_activate",
    ),
    path(
        "members/deactivate/<int:pk>/",
        MemberDeactivateView.as_view(),
        name="member_deactivate",
    ),
    path("what-we-do/", WhatWeDoListView.as_view(), name="what_we_do_list"),
    path("what-we-do/create/", WhatWeDoCreateView.as_view(), name="what_we_do_create"),
    path(
        "what-we-do/edit/<int:pk>/",
        WhatWeDoUpdateView.as_view(),
        name="what_we_do_edit",
    ),
    path(
        "what-we-do/delete/<int:pk>/",
        WhatWeDoDeleteView.as_view(),
        name="what_we_do_delete",
    ),
    path("event/", EventListView.as_view(), name="event_list"),
    path("event/detail/<int:pk>/", EventDetailView.as_view(), name="event_detail"),
    path("event/create/", EventCreateView.as_view(), name="event_create"),
    path("event/edit/<int:pk>/", EventUpdateView.as_view(), name="event_edit"),
    path("event/delete/<int:pk>/", EventDeleteView.as_view(), name="event_delete"),
    path("project/", ProjectListView.as_view(), name="project_list"),
    path("project/my/", MyProjectListView.as_view(), name="my_project"),
    path(
        "project/detail/<int:pk>/", ProjectDetailView.as_view(), name="project_detail"
    ),
    path("project/create/", ProjectCreateView.as_view(), name="project_create"),
    path("project/edit/<int:pk>/", ProjectUpdateView.as_view(), name="project_edit"),
    path(
        "project/delete/<int:pk>/", ProjectDeleteView.as_view(), name="project_delete"
    ),
    path("resource/", ResourceListView.as_view(), name="resource_list"),
    path(
        "resource/detail/<int:pk>/",
        ResourceDetailView.as_view(),
        name="resource_detail",
    ),
    path("resource/create/", ResourceCreateView.as_view(), name="resource_create"),
    path("resource/edit/<int:pk>/", ResourceUpdateView.as_view(), name="resource_edit"),
    path(
        "resource/delete/<int:pk>/",
        ResourceDeleteView.as_view(),
        name="resource_delete",
    ),
    path("session/", SessionListView.as_view(), name="session_list"),
    path(
        "session/detail/<int:pk>/", SessionDetailView.as_view(), name="session_detail"
    ),
    path("session/create/", SessionCreateView.as_view(), name="session_create"),
    path("session/edit/<int:pk>/", SessionUpdateView.as_view(), name="session_edit"),
    path(
        "session/delete/<int:pk>/",
        SessionDeleteView.as_view(),
        name="session_delete",
    ),
    path("attendance/", AttendanceListView.as_view(), name="attendance_list"),
    path("attendance/my/", MyAttendanceDetailView.as_view(), name="my_attendance"),
    path(
        "attendance/<int:pk>/", AttendanceDetailView.as_view(), name="attendance_detail"
    ),
]
