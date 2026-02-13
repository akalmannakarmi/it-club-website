from django.urls import path

from .views import (
    DashboardView,
    PageView,
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
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    ProjectListView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    ResourceListView,
    ResourceCreateView,
    ResourceUpdateView,
    ResourceDeleteView,
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("page/", PageView.as_view(), name="page_settings"),
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
    path("event/create/", EventCreateView.as_view(), name="event_create"),
    path("event/edit/<int:pk>/", EventUpdateView.as_view(), name="event_edit"),
    path("event/delete/<int:pk>/", EventDeleteView.as_view(), name="event_delete"),
    path("project/", ProjectListView.as_view(), name="project_list"),
    path("project/create/", ProjectCreateView.as_view(), name="project_create"),
    path("project/edit/<int:pk>/", ProjectUpdateView.as_view(), name="project_edit"),
    path(
        "project/delete/<int:pk>/", ProjectDeleteView.as_view(), name="project_delete"
    ),
    path("resource/", ResourceListView.as_view(), name="resource_list"),
    path("resource/create/", ResourceCreateView.as_view(), name="resource_create"),
    path("resource/edit/<int:pk>/", ResourceUpdateView.as_view(), name="resource_edit"),
    path(
        "resource/delete/<int:pk>/",
        ResourceDeleteView.as_view(),
        name="resource_delete",
    ),
]
