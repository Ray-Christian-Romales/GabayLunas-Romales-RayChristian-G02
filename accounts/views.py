from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("/")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. You can now log in.")
            return redirect("/login/")  # the named URL arrives in step 8
        messages.error(request, "Please fix the errors below.")
    return render(request, "accounts/register.html", {"form": form})