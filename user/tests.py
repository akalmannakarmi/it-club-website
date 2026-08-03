from unittest.mock import patch

from django.contrib.auth import authenticate
from django.test import TestCase
from django.urls import reverse

from .models import User


class RegistrationTests(TestCase):
    @patch("user.views.send_html_email")
    def test_registration_creates_inactive_member(self, mock_email):
        response = self.client.post(
            reverse("user:register"),
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@example.com",
                "phone": "9800000000",
                "batch": "2075",
                "faculty": "CSIT",
                "password": "S3curePass!",
                "confirm_password": "S3curePass!",
            },
        )
        self.assertRedirects(response, reverse("user:login"))
        user = User.objects.get(email="jane@example.com")
        self.assertFalse(user.is_active)
        self.assertTrue(user.groups.filter(name="Member").exists())


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="alice@example.com", password="Passw0rd!", first_name="Alice"
        )

    def test_active_user_can_login(self):
        response = self.client.post(
            reverse("user:login"),
            {"email": "alice@example.com", "password": "Passw0rd!"},
        )
        self.assertRedirects(response, reverse("home"))

    def test_wrong_password_rejected(self):
        response = self.client.post(
            reverse("user:login"),
            {"email": "alice@example.com", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password")

    def test_inactive_user_cannot_authenticate(self):
        User.objects.create_user(
            email="bob@example.com", password="Passw0rd!", is_active=False
        )
        self.assertIsNone(authenticate(email="bob@example.com", password="Passw0rd!"))

    def test_inactive_user_cannot_login(self):
        User.objects.create_user(
            email="bob@example.com", password="Passw0rd!", is_active=False
        )
        response = self.client.post(
            reverse("user:login"),
            {"email": "bob@example.com", "password": "Passw0rd!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password")


class UserModelTests(TestCase):
    def test_full_name_falls_back_to_email(self):
        user = User.objects.create_user(email="only@example.com")
        self.assertEqual(user.full_name, "only@example.com")
        self.assertEqual(str(user), "only@example.com")

    def test_full_name_uses_names(self):
        user = User.objects.create_user(
            email="named@example.com", first_name="Nina", last_name="Novak"
        )
        self.assertEqual(user.full_name, "Nina Novak")

    def test_superuser_joins_admin_group(self):
        admin = User.objects.create_superuser(
            email="root@example.com", password="R00tPass!"
        )
        self.assertTrue(admin.groups.filter(name="Admin").exists())
        self.assertTrue(admin.is_superuser)
