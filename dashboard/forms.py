from django import forms
from user.models import User
from pages.models import PageVisibility, WhatWeDo
from events.models import Event
from projects.models import Project
from resources.models import Resource


class PageForm(forms.ModelForm):
    class Meta:
        model = PageVisibility
        fields = "__all__"


class MemberForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "faculty",
            "batch",
            "is_active",
        ]


class WhatWeDoForm(forms.ModelForm):
    class Meta:
        model = WhatWeDo
        fields = "__all__"


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = "__all__"
