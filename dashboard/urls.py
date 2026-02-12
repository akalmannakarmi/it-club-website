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
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("page/", PageView.as_view(), name="page_settings"),
    path("members/", MemberListView.as_view(), name="member_list"),
    path("members/create/", MemberCreateView.as_view(), name="member_create"),
    path("members/edit/<int:member_id>/", MemberUpdateView.as_view(), name="member_edit"),
    path("members/delete/<int:member_id>/", MemberDeleteView.as_view(), name="member_delete"),
    path("members/activate/<int:member_id>/", MemberActivateView.as_view(), name="member_activate"),
    path("members/deactivate/<int:member_id>/", MemberDeactivateView.as_view(), name="member_deactivate"),

    path("what-we-do/", WhatWeDoListView.as_view(), name="what_we_do_list"),
    path("what-we-do/create/", WhatWeDoCreateView.as_view(), name="what_we_do_create"),
    path("what-we-do/edit/<int:pk>/", WhatWeDoUpdateView.as_view(), name="what_we_do_edit"),
    path("what-we-do/delete/<int:pk>/", WhatWeDoDeleteView.as_view(), name="what_we_do_delete"),
]
