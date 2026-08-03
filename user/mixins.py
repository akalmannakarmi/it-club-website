from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class GroupsRequiredMixin(LoginRequiredMixin):
    group_names = None

    def dispatch(self, request, *args, **kwargs):
        if not self.group_names:
            raise ValueError("group_names must be set")

        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        if not request.user.group_names.intersection(self.group_names):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(GroupsRequiredMixin):
    group_names = [
        "Admin",
    ]


class MemberRequiredMixin(GroupsRequiredMixin):
    group_names = ["Admin", "Member"]


class AdminOrOwnerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        if "Admin" in user.group_names:
            return super().dispatch(request, *args, **kwargs)

        if not hasattr(self, "get_object"):
            raise AttributeError("View must define get_object()")

        obj = self.get_object()

        # ---- Ownership checks ----
        if hasattr(obj, "user_id") and obj.user_id == user.id:
            return super().dispatch(request, *args, **kwargs)
        if hasattr(obj, "user") and obj.user == user:
            return super().dispatch(request, *args, **kwargs)
        if hasattr(obj, "supervisor") and obj.supervisor == user:
            return super().dispatch(request, *args, **kwargs)
        if hasattr(obj, "members"):
            members = getattr(obj, "members")
            try:
                if members.filter(id=user.id).exists():
                    return super().dispatch(request, *args, **kwargs)
            except Exception:
                pass

        raise PermissionDenied
