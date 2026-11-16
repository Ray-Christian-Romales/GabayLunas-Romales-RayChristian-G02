from django import forms
from django.forms import inlineformset_factory

from .models import Illness, IllnessSymptom, Symptom


class SymptomForm(forms.ModelForm):
    class Meta:
        model = Symptom
        fields = ["name", "body_part", "is_red_flag", "red_flag_message"]

    def clean(self):
        data = super().clean()
        if data.get("is_red_flag") and not (data.get("red_flag_message") or "").strip():
            self.add_error("red_flag_message", "A red-flag symptom needs a warning message.")
        return data


class IllnessForm(forms.ModelForm):
    class Meta:
        model = Illness
        fields = ["name", "description", "severity_level"]


IllnessSymptomFormSet = inlineformset_factory(
    Illness, IllnessSymptom, fields=["symptom", "match_weight"], extra=3, can_delete=True)


class SymptomCheckForm(forms.Form):
    symptoms = forms.ModelMultipleChoiceField(
        queryset=Symptom.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": "Select at least one symptom."},
    )
