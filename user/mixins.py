from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class GroupRequiredMixin(LoginRequiredMixin):
    group_name = None

    def dispatch(self, request, *args, **kwargs):
        if self.group_name is None:
            raise ValueError("group_name must be set")

        if not request.user.groups.filter(name=self.group_name).exists():
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(GroupRequiredMixin):
    group_name = "Admin"


class MemberRequiredMixin(GroupRequiredMixin):
    group_name = "Member"
