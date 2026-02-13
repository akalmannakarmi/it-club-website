import threading

_thread_locals = threading.local()


def get_current_user():
    user = getattr(_thread_locals, "user", None)
    if user and getattr(user, "is_authenticated", False):
        return user
    return None


class CurrentUserMiddleware:
    """
    Stores the current user in thread locals.
    Add this middleware in settings.py.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = getattr(request, "user", None)
        response = self.get_response(request)
        return response
