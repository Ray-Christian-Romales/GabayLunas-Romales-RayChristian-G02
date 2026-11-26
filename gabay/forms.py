from django import forms
from django.forms import inlineformset_factory

from .models import Illness, IllnessSymptom, Symptom


class SymptomForm(forms.ModelForm):
    class Meta:
        model = Symptom
        fields = ["name", "body_part", "is_red_flag", "red_flag_message"]

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())
        if len(name) < 3:
            raise forms.ValidationError("Name must be at least 3 characters.")
        qs = Symptom.objects.filter(name__iexact=name).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A symptom with this name already exists.")
        return name

    def clean(self):
        data = super().clean()
        if data.get("is_red_flag") and not (data.get("red_flag_message") or "").strip():
            self.add_error("red_flag_message", "A red-flag symptom needs a warning message.")
        return data


class IllnessForm(forms.ModelForm):
    class Meta:
        model = Illness
        fields = ["name", "description", "severity_level"]

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())
        if len(name) < 3:
            raise forms.ValidationError("Name must be at least 3 characters.")
        qs = Illness.objects.filter(name__iexact=name).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("An illness with this name already exists.")
        return name

    def clean_description(self):
        desc = " ".join(self.cleaned_data["description"].split())
        if len(desc) < 20:
            raise forms.ValidationError("Description must be at least 20 characters.")
        return desc


IllnessSymptomFormSet = inlineformset_factory(
    Illness, IllnessSymptom, fields=["symptom", "match_weight"], extra=3, can_delete=True)


class SymptomCheckForm(forms.Form):
    symptoms = forms.ModelMultipleChoiceField(
        queryset=Symptom.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": "Select at least one symptom."},
    )
