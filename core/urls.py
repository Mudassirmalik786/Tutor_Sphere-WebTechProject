from django.urls import path
from core import views

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing_page'),
    path('about/', views.AboutPageView.as_view(), name='about_page'),
    path('faq/', views.FAQPageView.as_view(), name='faq_page'),
]
