from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from .forms import IllnessForm, IllnessSymptomFormSet, SymptomForm
from .models import Illness, SearchLog, Symptom


# ---------- Reviewer: symptoms ----------
@role_required("REVIEWER")
def symptom_list(request):
    return render(request, "gabay/symptom_list.html", {"symptoms": Symptom.objects.all()})


def _symptom_form(request, symptom=None):
    form = SymptomForm(request.POST or None, instance=symptom)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Symptom saved.")
        return redirect("symptom_list")
    title = "Edit symptom" if symptom else "Add symptom"
    return render(request, "gabay/form.html", {"form": form, "title": title, "back": "symptom_list"})


@role_required("REVIEWER")
def symptom_create(request):
    return _symptom_form(request)


@role_required("REVIEWER")
def symptom_edit(request, pk):
    return _symptom_form(request, get_object_or_404(Symptom, pk=pk))


@role_required("REVIEWER")
@require_POST
def symptom_delete(request, pk):
    get_object_or_404(Symptom, pk=pk).delete()
    messages.success(request, "Symptom deleted.")
    return redirect("symptom_list")


# ---------- Reviewer: illnesses ----------
@role_required("REVIEWER")
def illness_list(request):
    illnesses = Illness.objects.select_related("submitted_by")
    return render(request, "gabay/illness_list.html", {"illnesses": illnesses})


def _illness_form(request, illness=None):
    form = IllnessForm(request.POST or None, instance=illness)
    formset = IllnessSymptomFormSet(request.POST or None, instance=illness or Illness())
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        rows = [x for x in formset.forms if x.cleaned_data and not x.cleaned_data.get("DELETE")]
        ids = [x.cleaned_data["symptom"].pk for x in rows]
        if not rows:
            messages.error(request, "Link at least one symptom.")
        elif len(ids) != len(set(ids)):
            messages.error(request, "Each symptom can be linked only once.")
        else:
            with transaction.atomic():
                obj = form.save(commit=False)
                obj.submitted_by = request.user
                obj.status = Illness.Status.PENDING
                obj.reviewed_by = None
                obj.reviewed_at = None
                obj.review_notes = ""
                obj.save()
                formset.instance = obj
                formset.save()
            messages.success(request, "Illness saved and set to PENDING.")
            return redirect("illness_list")
    title = "Edit illness" if illness else "Add illness"
    return render(request, "gabay/form.html", {"form": form, "formset": formset, "title": title, "back": "illness_list"})


@role_required("REVIEWER")
def illness_create(request):
    return _illness_form(request)


@role_required("REVIEWER")
def illness_edit(request, pk):
    return _illness_form(request, get_object_or_404(Illness, pk=pk))


@role_required("REVIEWER")
@require_POST
def illness_delete(request, pk):
    get_object_or_404(Illness, pk=pk).delete()
    messages.success(request, "Illness deleted.")
    return redirect("illness_list")


@role_required("REVIEWER")
@require_POST
def illness_approve(request, pk):
    illness = get_object_or_404(Illness, pk=pk, status=Illness.Status.PENDING)
    if illness.submitted_by_id == request.user.id:
        messages.error(request, "Another reviewer must approve your entry.")
    else:
        with transaction.atomic():
            illness.status = Illness.Status.APPROVED
            illness.reviewed_by = request.user
            illness.reviewed_at = timezone.now()
            illness.save()
        messages.success(request, "Illness approved.")
    return redirect("illness_list")
