from datetime import date

from django.test import TestCase

from attendance.models import Session
from user.models import User


class SessionAttendanceTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            email="attend@example.com", password="pass1234"
        )
        self.s1 = Session.objects.create(title="S1", date=date(2026, 8, 1))
        self.s2 = Session.objects.create(title="S2", date=date(2026, 8, 2))

    def test_add_attendee(self):
        self.s1.attendees.add(self.member)
        self.assertEqual(self.s1.attendees.count(), 1)
        self.assertIn(self.s1, self.member.attended_sessions.all())

    def test_remove_attendee(self):
        self.s1.attendees.add(self.member)
        self.s1.attendees.remove(self.member)
        self.assertEqual(self.s1.attendees.count(), 0)

    def test_member_attended_sessions_across_sessions(self):
        self.s1.attendees.add(self.member)
        self.s2.attendees.add(self.member)
        self.assertEqual(self.member.attended_sessions.count(), 2)
