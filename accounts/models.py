from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", "REVIEWER")
        return self.create_user(email, password, **extra)


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = "CITIZEN", "Citizen User"
        REVIEWER = "REVIEWER", "Medical Reviewer / Admin"

    BLOOD_TYPES = [(b, b) for b in ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-")]

    username = None
    email = models.EmailField("email address", unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CITIZEN)
    contact_number = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES, blank=True)
    medical_allergies = models.TextField(blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email