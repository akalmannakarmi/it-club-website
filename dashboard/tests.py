from unittest.mock import patch

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from attendance.models import Session
from events.models import Event
from projects.models import Project
from resources.models import Resource
from user.models import User


def create_user(email, password="pass1234", **kwargs):
    return User.objects.create_user(email=email, password=password, **kwargs)


def add_to_group(user, name):
    group, _ = Group.objects.get_or_create(name=name)
    user.groups.add(group)
    return user


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.admin = add_to_group(create_user(email="admin@example.com"), "Admin")
        self.member = add_to_group(create_user(email="member@example.com"), "Member")

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertRedirects(response, f"{reverse('user:login')}?next=/dashboard/")

    def test_member_can_view_dashboard_home(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)

    def test_member_blocked_from_admin_only_view(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("dashboard:member_list"))
        self.assertEqual(response.status_code, 403)

    def test_admin_allowed_on_admin_only_view(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("dashboard:member_list"))
        self.assertEqual(response.status_code, 200)


class EventCrudTests(TestCase):
    def setUp(self):
        self.admin = add_to_group(create_user(email="admin2@example.com"), "Admin")
        self.member = add_to_group(create_user(email="member2@example.com"), "Member")
        self.client.force_login(self.admin)

    def test_create_event(self):
        response = self.client.post(
            reverse("dashboard:event_create"),
            {
                "title": "Hackathon",
                "date": "2026-08-02T10:00",
                "order": "0",
                "display": "on",
            },
        )
        self.assertRedirects(response, reverse("dashboard:event_list"))
        self.assertTrue(Event.objects.filter(title="Hackathon").exists())

    def test_member_cannot_create_event(self):
        self.client.force_login(self.member)
        response = self.client.post(
            reverse("dashboard:event_create"),
            {"title": "Nope", "date": "2026-08-02T10:00", "order": "0"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Event.objects.filter(title="Nope").exists())

    def test_update_event(self):
        event = Event.objects.create(title="Old", date=timezone.now(), order=0)
        response = self.client.post(
            reverse("dashboard:event_edit", args=[event.id]),
            {"title": "New", "date": "2026-08-03T10:00", "order": "0"},
        )
        self.assertRedirects(response, reverse("dashboard:event_list"))
        event.refresh_from_db()
        self.assertEqual(event.title, "New")

    def test_delete_event(self):
        event = Event.objects.create(title="Gone", date=timezone.now(), order=0)
        response = self.client.post(reverse("dashboard:event_delete", args=[event.id]))
        self.assertRedirects(response, reverse("dashboard:event_list"))
        self.assertFalse(Event.objects.filter(id=event.id).exists())


class ProjectCrudTests(TestCase):
    def setUp(self):
        self.admin = add_to_group(create_user(email="admin3@example.com"), "Admin")
        self.member = add_to_group(create_user(email="member3@example.com"), "Member")
        self.client.force_login(self.admin)

    def test_create_project(self):
        response = self.client.post(
            reverse("dashboard:project_create"),
            {
                "title": "Club Site",
                "members": [self.member.id],
                "order": "0",
                "display": "on",
            },
        )
        self.assertRedirects(response, reverse("dashboard:project_list"))
        project = Project.objects.get(title="Club Site")
        self.assertIn(self.member, project.members.all())

    def test_update_project(self):
        project = Project.objects.create(title="Old Project", order=0)
        project.members.add(self.member)
        response = self.client.post(
            reverse("dashboard:project_edit", args=[project.id]),
            {"title": "New Project", "members": [self.member.id], "order": "0"},
        )
        self.assertRedirects(response, reverse("dashboard:project_list"))
        project.refresh_from_db()
        self.assertEqual(project.title, "New Project")

    def test_delete_project(self):
        project = Project.objects.create(title="Gone Project", order=0)
        response = self.client.post(
            reverse("dashboard:project_delete", args=[project.id])
        )
        self.assertRedirects(response, reverse("dashboard:project_list"))
        self.assertFalse(Project.objects.filter(id=project.id).exists())


class ResourceCrudTests(TestCase):
    def setUp(self):
        self.admin = add_to_group(create_user(email="admin4@example.com"), "Admin")
        self.client.force_login(self.admin)

    def test_create_resource(self):
        response = self.client.post(
            reverse("dashboard:resource_create"),
            {"title": "Django Docs", "order": "0", "display": "on"},
        )
        self.assertRedirects(response, reverse("dashboard:resource_list"))
        self.assertTrue(Resource.objects.filter(title="Django Docs").exists())

    def test_update_and_delete_resource(self):
        resource = Resource.objects.create(title="Old", order=0)
        self.client.post(
            reverse("dashboard:resource_edit", args=[resource.id]),
            {"title": "Updated", "order": "0"},
        )
        resource.refresh_from_db()
        self.assertEqual(resource.title, "Updated")
        self.client.post(reverse("dashboard:resource_delete", args=[resource.id]))
        self.assertFalse(Resource.objects.filter(id=resource.id).exists())


class SessionCrudTests(TestCase):
    def setUp(self):
        self.admin = add_to_group(create_user(email="admin5@example.com"), "Admin")
        self.member = add_to_group(create_user(email="member5@example.com"), "Member")
        self.client.force_login(self.admin)

    def test_create_session(self):
        response = self.client.post(
            reverse("dashboard:session_create"),
            {
                "title": "Python Workshop",
                "date": "2026-08-02",
                "attendees": [self.member.id],
            },
        )
        self.assertRedirects(response, reverse("dashboard:session_list"))
        session = Session.objects.get(title="Python Workshop")
        self.assertIn(self.member, session.attendees.all())

    def test_update_session(self):
        session = Session.objects.create(title="Old Session", date="2026-08-02")
        session.attendees.add(self.member)
        response = self.client.post(
            reverse("dashboard:session_edit", args=[session.id]),
            {
                "title": "New Session",
                "date": "2026-08-03",
                "attendees": [self.member.id],
            },
        )
        self.assertRedirects(response, reverse("dashboard:session_list"))
        session.refresh_from_db()
        self.assertEqual(session.title, "New Session")

    def test_delete_session(self):
        session = Session.objects.create(title="Gone Session", date="2026-08-02")
        response = self.client.post(
            reverse("dashboard:session_delete", args=[session.id])
        )
        self.assertRedirects(response, reverse("dashboard:session_list"))
        self.assertFalse(Session.objects.filter(id=session.id).exists())


class DashboardRenderTests(TestCase):
    def setUp(self):
        self.admin = add_to_group(create_user(email="admin7@example.com"), "Admin")
        self.member = add_to_group(create_user(email="member7@example.com"), "Member")
        self.member2 = add_to_group(create_user(email="member8@example.com"), "Member")

    def test_member_list_pages_render(self):
        self.client.force_login(self.member)
        for name in [
            "dashboard:event_list",
            "dashboard:resource_list",
            "dashboard:session_list",
            "dashboard:my_project",
            "dashboard:my_attendance",
        ]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, msg=name)

    def test_admin_list_pages_render(self):
        self.client.force_login(self.admin)
        for name in [
            "dashboard:member_list",
            "dashboard:what_we_do_list",
            "dashboard:project_list",
            "dashboard:audit_list",
            "dashboard:attendance_list",
            "dashboard:event_list",
        ]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, msg=name)

        attendance_url = reverse("dashboard:attendance_detail", args=[self.member2.id])
        self.assertEqual(self.client.get(attendance_url).status_code, 200)

        event = Event.objects.create(title="Detail", date=timezone.now(), order=0)
        event_url = reverse("dashboard:event_detail", args=[event.id])
        self.assertEqual(self.client.get(event_url).status_code, 200)

    def test_admin_form_pages_render(self):
        self.client.force_login(self.admin)
        for name in [
            "dashboard:event_create",
            "dashboard:project_create",
            "dashboard:resource_create",
            "dashboard:session_create",
            "dashboard:what_we_do_create",
            "dashboard:member_create",
        ]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, msg=name)


class MemberActivationTests(TestCase):
    def setUp(self):
        self.admin = add_to_group(create_user(email="admin6@example.com"), "Admin")
        self.member = User.objects.create_user(
            email="act@example.com", password="pass1234", is_active=False
        )
        self.client.force_login(self.admin)

    @patch("dashboard.views.send_html_email")
    def test_activate_sets_active(self, mock_email):
        self.client.post(reverse("dashboard:member_activate", args=[self.member.id]))
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_active)

    @patch("dashboard.views.send_html_email")
    def test_deactivate_sets_inactive(self, mock_email):
        self.member.is_active = True
        self.member.save()
        self.client.post(reverse("dashboard:member_deactivate", args=[self.member.id]))
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)

    @patch("dashboard.views.send_html_email")
    def test_activate_blocks_open_redirect(self, mock_email):
        response = self.client.post(
            reverse("dashboard:member_activate", args=[self.member.id]),
            {"next": "https://evil.example.com"},
        )
        self.assertRedirects(response, reverse("dashboard:member_list"))

    @patch("dashboard.views.send_html_email")
    def test_activate_allows_same_host_next(self, mock_email):
        response = self.client.post(
            reverse("dashboard:member_activate", args=[self.member.id]),
            {"next": "/dashboard/audit/"},
        )
        self.assertRedirects(response, "/dashboard/audit/")
