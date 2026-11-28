from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import SymptomForm
from .models import Illness, IllnessSymptom, SearchLog, Symptom

User = get_user_model()
PW = "Use-A-Demo-Password-1"


def mk(email, role):
    return User.objects.create_user(
        email=email, password=PW, role=role, first_name="Test", last_name="User"
    )


class Base(TestCase):
    def setUp(self):
        self.cit = mk("c1@t.com", "CITIZEN")
        self.cit2 = mk("c2@t.com", "CITIZEN")
        self.rev1 = mk("r1@t.com", "REVIEWER")
        self.rev2 = mk("r2@t.com", "REVIEWER")
        self.fever = Symptom.objects.create(name="Fever", body_part="Body")
        self.flu = Illness.objects.create(
            name="Influenza",
            description="Viral infection with fever.",
            severity_level="MODERATE",
            status="PENDING",
            submitted_by=self.rev1,
        )
        IllnessSymptom.objects.create(illness=self.flu, symptom=self.fever, match_weight=3)


class GabayTests(Base):
    def test_valid_check_saves_and_redirects(self):
        self.client.force_login(self.cit)
        r = self.client.post(reverse("gabay_check"), {"symptoms": [self.fever.pk]})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(SearchLog.objects.filter(user=self.cit).count(), 1)

    def test_empty_check_is_rejected(self):
        self.client.force_login(self.cit)
        r = self.client.post(reverse("gabay_check"), {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(SearchLog.objects.count(), 0)

    def test_login_required(self):
        for name in ["gabay_check", "history", "symptom_list", "illness_list"]:
            with self.subTest(name):
                r = self.client.get(reverse(name))
                self.assertEqual(r.status_code, 302)
                self.assertIn("login", r["Location"])

    def test_citizen_blocked_from_reviewer_pages(self):
        self.client.force_login(self.cit)
        self.assertNotEqual(self.client.get(reverse("symptom_list")).status_code, 200)

    def test_reviewer_blocked_from_gabay(self):
        self.client.force_login(self.rev1)
        self.assertNotEqual(self.client.get(reverse("gabay_check")).status_code, 200)

    def test_cannot_delete_another_users_history(self):
        log = SearchLog.objects.create(user=self.cit2, search_type="SYMPTOM", query_text="Fever")
        self.client.force_login(self.cit)
        r = self.client.post(reverse("history_delete", args=[log.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(SearchLog.objects.filter(pk=log.pk).exists())

    def test_history_shows_only_own(self):
        SearchLog.objects.create(user=self.cit2, search_type="SYMPTOM", query_text="SECRET-QUERY")
        self.client.force_login(self.cit)
        self.assertNotContains(self.client.get(reverse("history")), "SECRET-QUERY")

    def test_self_approval_blocked(self):
        self.client.force_login(self.rev1)
        self.client.post(reverse("illness_approve", args=[self.flu.pk]))
        self.flu.refresh_from_db()
        self.assertEqual(self.flu.status, "PENDING")

    def test_other_reviewer_can_approve(self):
        self.client.force_login(self.rev2)
        self.client.post(reverse("illness_approve", args=[self.flu.pk]))
        self.flu.refresh_from_db()
        self.assertEqual(self.flu.status, "APPROVED")

    def test_red_flag_needs_message(self):
        form = SymptomForm(
            data={
                "name": "Chest pain",
                "body_part": "Chest",
                "is_red_flag": True,
                "red_flag_message": "",
            }
        )
        self.assertFalse(form.is_valid())

    def test_delete_by_get_not_allowed(self):
        self.client.force_login(self.rev1)
        r = self.client.get(reverse("illness_delete", args=[self.flu.pk]))
        self.assertEqual(r.status_code, 405)

    def test_refresh_does_not_duplicate_history(self):
        self.client.force_login(self.cit)
        r = self.client.post(reverse("gabay_check"), {"symptoms": [self.fever.pk]}, follow=True)
        self.client.get(r.redirect_chain[-1][0])
        self.assertEqual(SearchLog.objects.filter(user=self.cit).count(), 1)

    def test_custom_404_page(self):
        r = self.client.get("/no-such-page/")
        self.assertEqual(r.status_code, 404)
        self.assertTemplateUsed(r, "404.html")
