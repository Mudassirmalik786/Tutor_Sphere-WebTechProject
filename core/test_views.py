from django.test import TestCase
from django.urls import reverse

from core.models import About, FrequentlyAskedQuestion


class LandingPageTestCases(TestCase):
    """
    Test cases for the landing page view.
    """

    def test_landing_page_status_code(self):
        """Test the status code of the landing page."""
        response = self.client.get(reverse('landing_page'))
        self.assertEqual(response.status_code, 200)

    def test_landing_page_template(self):
        """Test the template used to render the landing page."""
        response = self.client.get(reverse('landing_page'))
        self.assertTemplateUsed(response, 'core/index.html')


class AboutPageTestCases(TestCase):
    """
    Test cases for the about page view.
    """

    def setUp(self):
        """Create an About instance for the test cases."""
        About.objects.create(
            title="About Test Title",
            content="About Test Text",
            is_active=True
        )

        About.objects.create(
            title="Inactive About Title",
            content="Inactive About Text",
            is_active=False
        )

    def test_about_page_status_code(self):
        """Test the status code of the about page."""
        response = self.client.get(reverse('about_page'))
        self.assertEqual(response.status_code, 200)

    def test_about_page_template(self):
        """Test the template used to render the about page."""
        response = self.client.get(reverse('about_page'))
        self.assertTemplateUsed(response, 'core/about.html')

    def test_about_page_context(self):
        """Test the context data of the about page."""
        response = self.client.get(reverse('about_page'))
        self.assertContains(response, "About Test Title")
        self.assertContains(response, "About Test Text")
        self.assertTrue(response.context['object'].is_active)


class FAQPageTestCases(TestCase):
    """
    Test cases for the frequently asked questions page view.
    """

    def setUp(self):
        """Create FrequentlyAskedQuestion instances for the test cases."""
        FrequentlyAskedQuestion.objects.create(
            question="FAQ Test Question 1",
            answer="FAQ Test Answer 1"
        )

        FrequentlyAskedQuestion.objects.create(
            question="FAQ Test Question 2",
            answer="FAQ Test Answer 2"
        )

    def test_faq_page_status_code(self):
        """Test the status code of the frequently asked questions page."""
        response = self.client.get(reverse('faq_page'))
        self.assertEqual(response.status_code, 200)

    def test_faq_page_template(self):
        """Test the template used to render the FAQ page."""
        response = self.client.get(reverse('faq_page'))
        self.assertTemplateUsed(response, 'core/faq.html')

    def test_faq_page_context(self):
        """Test the context data of the frequently asked questions page."""
        response = self.client.get(reverse('faq_page'))
        self.assertContains(response, "FAQ Test Question 1")
        self.assertContains(response, "FAQ Test Answer 1")
        self.assertContains(response, "FAQ Test Question 2")
        self.assertContains(response, "FAQ Test Answer 2")
        self.assertEqual(len(response.context['faqs']), 2)
