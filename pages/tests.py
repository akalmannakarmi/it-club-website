from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from pages.models import PageSettings


class HomepageTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_homepage_renders_with_default_settings(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, PageSettings().org_name)

    def test_hidden_sections_do_not_render(self):
        settings, _ = PageSettings.objects.get_or_create(pk=1)
        for flag in [
            "show_banner",
            "show_about",
            "show_whatwedo",
            "show_upcoming",
            "show_projects",
            "show_resources",
            "show_events",
            "show_footer",
        ]:
            setattr(settings, flag, False)
        settings.save()
        cache.delete("page_settings")

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        for marker in [
            "About Club",
            "Upcoming Activities",
            "What We Do</h2>",
            "Projects</h2>",
            "Learning Resources",
            "Major Events</h2>",
            "All rights reserved",
        ]:
            self.assertNotContains(response, marker)

    def test_events_page_renders(self):
        response = self.client.get(reverse("events"))
        self.assertEqual(response.status_code, 200)

    def test_resources_page_renders(self):
        response = self.client.get(reverse("resources"))
        self.assertEqual(response.status_code, 200)
