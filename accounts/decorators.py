from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

DASHBOARD_BY_ROLE = {
    "CITIZEN": "citizen_dashboard",
    "REVIEWER": "reviewer_dashboard",
}


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if request.user.role not in allowed_roles:
                messages.error(request, "You do not have access to that page.")
                return redirect(DASHBOARD_BY_ROLE[request.user.role])
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator