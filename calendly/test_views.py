from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from tutor_market.models import Tutor


class ConnectCalendlyTestCases(TestCase):
    """Test cases for the connect_calendly view."""

    def setUp(self):
        """Set up the test case."""
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        self.tutor = Tutor.objects.create(
            user=self.user,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True
        )

    def test_connect_calendly_login_required(self):
        """Test that the view redirects to the login page if the user is not
        authenticated."""
        self.client.logout()
        response = self.client.get(reverse('connect_calendly'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_connect_calendly(self):
        """
        Test case for the 'connect_calendly' view.
        """
        response = self.client.get(reverse('connect_calendly'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('https://calendly.com/oauth/authorize', response.url)


class CalendlyAuthTestCases(TestCase):
    """Test cases for the calendly_auth view."""

    def setUp(self):
        """Set up the test case."""
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_calendly_auth_login_required(self):
        """Test that the view redirects to the login page if the user is not
        authenticated."""
        self.client.logout()
        response = self.client.get(reverse('calendly_auth'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


class DisconnectCalendlyTestCases(TestCase):
    """Test cases for the disconnect_calendly view."""

    def setUp(self):
        """Set up the test case."""
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        self.tutor = Tutor.objects.create(
            user=self.user,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True
        )

    def test_disconnect_calendly_login_required(self):
        """
        Test that the view redirects to the login page if the user is not
        authenticated.
        """
        self.client.logout()
        response = self.client.get(
            reverse('disconnect_calendly', kwargs={'pk': self.tutor.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_disconnect_calendly(self):
        """
        Test case for the 'disconnect_calendly' view.
        """
        response = self.client.get(
            reverse('disconnect_calendly', kwargs={'pk': self.tutor.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(Tutor.objects.get(
            pk=self.tutor.pk).calendly_access_token)
        self.assertIsNone(Tutor.objects.get(
            pk=self.tutor.pk).calendly_refresh_token)
        self.assertIsNone(Tutor.objects.get(
            pk=self.tutor.pk).calendly_token_expires_at)
