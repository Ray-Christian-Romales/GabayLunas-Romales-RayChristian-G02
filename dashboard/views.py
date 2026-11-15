from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.decorators import DASHBOARD_BY_ROLE, role_required


@login_required
def dashboard_redirect(request):
    return redirect(DASHBOARD_BY_ROLE[request.user.role])


@role_required("CITIZEN")
def citizen_dashboard(request):
    return render(request, "dashboard/citizen.html")


@role_required("REVIEWER")
def reviewer_dashboard(request):
    return render(request, "dashboard/reviewer.html")