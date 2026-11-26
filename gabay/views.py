from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from .forms import IllnessForm, IllnessSymptomFormSet, SymptomCheckForm, SymptomForm
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


@role_required("REVIEWER")
@require_POST
def illness_reject(request, pk):
    illness = get_object_or_404(Illness, pk=pk, status=Illness.Status.PENDING)
    notes = request.POST.get("review_notes", "").strip()
    if illness.submitted_by_id == request.user.pk:
        messages.error(request, "Another reviewer must review your entry.")
    elif len(notes) < 5:
        messages.error(request, "Rejection notes are required (at least 5 characters).")
    else:
        with transaction.atomic():
            illness.status = Illness.Status.REJECTED
            illness.reviewed_by = request.user
            illness.reviewed_at = timezone.now()
            illness.review_notes = notes
            illness.save()
        messages.success(request, "Illness rejected.")
    return redirect("illness_list")

# ---------- Citizen: Gabay ----------
@role_required("CITIZEN")
def gabay_check(request):
    form = SymptomCheckForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        symptoms = list(form.cleaned_data["symptoms"])
        red_flags = [s for s in symptoms if s.is_red_flag]
        SearchLog.objects.create(
            user=request.user, search_type="SYMPTOM",
            query_text=", ".join(s.name for s in symptoms)[:255],
            red_flag_triggered=bool(red_flags))
        qs = "&".join(f"s={s.pk}" for s in symptoms)
        return redirect(f"{reverse('gabay_results')}?{qs}")
    return render(request, "gabay/check.html", {"form": form})


@role_required("CITIZEN")
def gabay_results(request):
    ids = [int(i) for i in request.GET.getlist("s") if i.isdigit()]
    symptoms = list(Symptom.objects.filter(pk__in=ids))
    if not symptoms:
        messages.error(request, "Select at least one symptom.")
        return redirect("gabay_check")
    symptom_ids = [s.pk for s in symptoms]
    red_flags = [s for s in symptoms if s.is_red_flag]
    found = (Illness.public
             .filter(illness_links__symptom_id__in=symptom_ids)
             .distinct()
             .prefetch_related("illness_links"))
    results = []
    for i in found:
        links = list(i.illness_links.all())
        i.score = sum(l.match_weight for l in links if l.symptom_id in symptom_ids)
        i.total = sum(l.match_weight for l in links)
        i.match_pct = round(i.score * 100 / i.total)
        results.append(i)
    results.sort(key=lambda i: (-i.score, -i.match_pct, i.name))
    results = results[:5]
    advisory = bool(results) and not red_flags and results[0].severity_level == "MODERATE"
    return render(request, "gabay/results.html",
                  {"results": results, "red_flags": red_flags, "advisory": advisory})


@role_required("CITIZEN")
def history_list(request):
    return render(request, "gabay/history.html", {"logs": request.user.search_logs.all()})


@role_required("CITIZEN")
@require_POST
def history_delete(request, pk):
    get_object_or_404(SearchLog, pk=pk, user=request.user).delete()
    messages.success(request, "Search deleted.")
    return redirect("history")


@role_required("CITIZEN")
@require_POST
def history_clear(request):
    request.user.search_logs.all().delete()
    messages.success(request, "History cleared.")
    return redirect("history")
