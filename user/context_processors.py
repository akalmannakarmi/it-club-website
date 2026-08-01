from django.http import HttpRequest


def user_group(request: HttpRequest):
    context = {}
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return context
    names = user.group_names
    context["is_admin"] = "Admin" in names
    context["is_member"] = "Member" in names
    return context
