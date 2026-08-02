from django.core.cache import cache
from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from pages.models import PageSettings
from pages.templatetags.math_filters import multiply, split, strip
from events.models import Event
from projects.models import Project
from resources.models import Resource


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
            "Community of builders",
            "The story behind",
            "Ways to get involved",
            "Upcoming Activities",
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

    def test_projects_page_renders(self):
        response = self.client.get(reverse("projects"))
        self.assertEqual(response.status_code, 200)


class NavigationTests(TestCase):
    def test_homepage_nav_uses_in_page_anchors(self):
        response = self.client.get(reverse("home"))
        content = response.content.decode()
        self.assertIn('href="#about"', content)
        self.assertIn('href="#what-we-do"', content)

    def test_list_page_nav_links_back_to_home_sections(self):
        response = self.client.get(reverse("projects"))
        content = response.content.decode()
        self.assertIn('href="/#about"', content)
        self.assertIn('href="/#what-we-do"', content)
        self.assertNotIn('href="#about"', content)

    def test_list_page_nav_highlights_current_page(self):
        for url, expected in [
            (reverse("projects"), 'href="/projects/" class="nav-link'),
            (reverse("events"), 'href="/events/" class="nav-link'),
            (reverse("resources"), 'href="/resource/" class="nav-link'),
        ]:
            response = self.client.get(url)
            content = response.content.decode()
            self.assertIn(expected, content)
            self.assertIn(' active"', content)


class DetailPageTests(TestCase):
    def test_event_detail_renders(self):
        event = Event(title="Test Event", date=timezone.now(), display=True)
        event.save(no_audit=True)
        response = self.client.get(reverse("event_detail", args=[event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Event")

    def test_hidden_event_detail_404(self):
        event = Event(title="Hidden Event", date=timezone.now(), display=False)
        event.save(no_audit=True)
        response = self.client.get(reverse("event_detail", args=[event.pk]))
        self.assertEqual(response.status_code, 404)

    def test_project_detail_renders(self):
        project = Project(title="Test Project", display=True)
        project.save(no_audit=True)
        response = self.client.get(reverse("project_detail", args=[project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Project")

    def test_resource_detail_renders(self):
        resource = Resource(title="Test Resource", display=True)
        resource.save(no_audit=True)
        response = self.client.get(reverse("resource_detail", args=[resource.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Resource")


class MathFilterTests(TestCase):
    def test_multiply(self):
        self.assertEqual(multiply(3, 8), 24)

    def test_split_default_separator(self):
        self.assertEqual(
            split("Python, Django, React JS"), ["Python", "Django", "React JS"]
        )

    def test_split_strips_whitespace(self):
        self.assertEqual(split("a, b ,  c"), ["a", "b", "c"])

    def test_split_empty_value(self):
        self.assertEqual(split(None), [])
        self.assertEqual(split(""), [])

    def test_split_renders_in_template(self):
        template = Template(
            "{% load math_filters %}"
            "{% for tech in value|split:',' %}{{ tech }}|{% endfor %}"
        )
        rendered = template.render(Context({"value": "Django,  Tailwind"}))
        self.assertEqual(rendered, "Django|Tailwind|")

    def test_strip(self):
        self.assertEqual(strip("  x  "), "x")
        self.assertEqual(strip(None), None)
