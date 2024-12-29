from django.http.response import HttpResponse as HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from core.models import About, FrequentlyAskedQuestion


class LandingPageView(TemplateView):
    """
    A view that renders the landing page template.
    """
    template_name = 'core/index.html'


class AboutPageView(DetailView):
    """
    A view that renders the about page template and retrieves the active About
    instance.
    """
    model = About
    template_name = "core/about.html"

    def get_object(self):
        """
        Retrieve the active About instance.

        Returns:
            About: The active About instance.
        """
        return About.objects.filter(is_active=True).first()


class FAQPageView(ListView):
    """
    A view that renders the frequently asked questions page template and
    retrieves all FAQs.
    """
    model = FrequentlyAskedQuestion
    template_name = "core/faq.html"
    context_object_name = "faqs"
