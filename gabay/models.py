from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ApprovedManager(models.Manager):
    # Citizen-facing reads use this: APPROVED rows only (BR-07)
    def get_queryset(self):
        return super().get_queryset().filter(status="APPROVED")


class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    body_part = models.CharField(max_length=50)
    is_red_flag = models.BooleanField(default=False)
    red_flag_message = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["body_part", "name"]

    def __str__(self):
        return self.name


class Illness(models.Model):
    class Severity(models.TextChoices):
        MILD = "MILD", "Mild"
        MODERATE = "MODERATE", "Moderate"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    severity_level = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MILD)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="submitted_illnesses")
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_illnesses")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    symptoms = models.ManyToManyField(Symptom, through="IllnessSymptom", related_name="illnesses")

    objects = models.Manager()
    public = ApprovedManager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class IllnessSymptom(models.Model):
    illness = models.ForeignKey(Illness, on_delete=models.CASCADE, related_name="illness_links")
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE, related_name="symptom_links")
    match_weight = models.PositiveSmallIntegerField(
        choices=[(1, "1 - rare"), (2, "2 - occasional"), (3, "3 - common")],
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
    )

    class Meta:
        constraints = [models.UniqueConstraint(fields=["illness", "symptom"], name="uq_illness_symptom")]


class SearchLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="search_logs")
    search_type = models.CharField(max_length=10, default="SYMPTOM")
    query_text = models.CharField(max_length=255)
    red_flag_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
