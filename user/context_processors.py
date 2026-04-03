from django.http import HttpRequest


def user_group(request: HttpRequest):
    context = {}
    if request.user.groups.filter(name="Admin").exists():
        context["is_admin"] = True
    if request.user.groups.filter(name="Member").exists():
        context["is_member"] = True
    return context
