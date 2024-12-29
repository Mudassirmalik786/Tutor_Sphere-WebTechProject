from datetime import timedelta, timezone
from django.utils import timezone
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from booking.models import Payment, TutoringSession
from gipfel_tutor import settings
from tutor_market.models import Subject, Tutor


class ScheduleSuccessViewTestCases(TestCase):
    """
    Test cases for the schedule success view.
    """

    def setUp(self):
        """Create a TutoringSession instance for the test cases."""

        self.user = User.objects.create_user(
            username='test_user', password='test_password'
        )

        self.tutor = Tutor.objects.create(
            user=self.user,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True
        )

        self.subject = Subject.objects.create(name='Mathematics')

        self.session = TutoringSession.objects.create(
            tutor=self.tutor,
            student=self.user,
            price=Decimal('50.00'),
            payment_complete=False,
            subject=self.subject,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            created_at=timezone.now(),
            location_url='https://example.com/location',
            session_name='Math Tutoring Session',
            event_uri='event_uri_example',
            invitee_uri='invitee_uri_example',
            cancel_url='https://example.com/cancel',
            reschedule_url='https://example.com/reschedule',
            invitee_email='student@example.com',
            invitee_notes='Please bring your textbook.',
            session_status='scheduled'
        )

    def test_schedule_success_status_code(self):
        """Test the status code of the schedule success page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(
            reverse('schedule_success', kwargs={'pk': self.session.pk}))
        self.assertEqual(response.status_code, 200)

    def test_schedule_success_template(self):
        """Test the template used to render the schedule success page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(
            reverse('schedule_success', kwargs={'pk': self.session.pk}))
        self.assertTemplateUsed(response, 'booking/schedule_success.html')

    def test_schedule_success_login_required(self):
        """
        Test that the user must be logged in to access the schedule
        success page.
        """
        response = self.client.get(
            reverse('schedule_success', kwargs={'pk': self.session.pk}))
        self.assertEqual(response.status_code, 302)

    def test_schedule_success_context(self):
        """Test the context of the schedule success page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(
            reverse('schedule_success', kwargs={'pk': self.session.pk}))
        self.assertEqual(response.context['session'], self.session)


class PaymentViewTestCases(TestCase):
    """
    Test cases for the payment view.
    """

    def setUp(self):
        """Create a TutoringSession instance for the test cases."""

        self.user = User.objects.create_user(
            username='test_user', password='test_password'
        )

        self.tutor = Tutor.objects.create(
            user=self.user,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True
        )

        self.subject = Subject.objects.create(name='Mathematics')

        self.session = TutoringSession.objects.create(
            tutor=self.tutor,
            student=self.user,
            price=Decimal('50.00'),
            payment_complete=False,
            subject=self.subject,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            created_at=timezone.now(),
            location_url='https://example.com/location',
            session_name='Math Tutoring Session',
            event_uri='event_uri_example',
            invitee_uri='invitee_uri_example',
            cancel_url='https://example.com/cancel',
            reschedule_url='https://example.com/reschedule',
        )

    def test_payment_status_code(self):
        """Test the status code of the payment page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(
            reverse('payments', kwargs={'pk': self.session.pk}))
        self.assertEqual(response.status_code, 200)

    def test_payment_template(self):
        """Test the template used to render the payment page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(
            reverse('payments', kwargs={'pk': self.session.pk}))
        self.assertTemplateUsed(response, 'booking/payment.html')

    def test_payment_login_required(self):
        """
        Test that the user must be logged in to access the payment
        page.
        """
        response = self.client.get(
            reverse('payments', kwargs={'pk': self.session.pk}))
        self.assertEqual(response.status_code, 302)

    def test_payment_context(self):
        """Test the context of the payment page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(
            reverse('payments', kwargs={'pk': 1}))
        self.assertEqual(response.context['sessions'][0], self.session)
        self.assertEqual(response.context['session_ids'][0], '1')
        self.assertEqual(response.context['total_price'], Decimal('50.00'))
        self.assertEqual(
            response.context['STRIPE_PUBLIC_KEY'], settings.STRIPE_PUBLIC_KEY)
        self.assertEqual(
            response.context['development'],
            'True' if settings.DEVELOPMENT else 'False'
        )

    def test_no_sessions_to_pay_for(self):
        """
        Test that the payment page displays a message when the user
        has no sessions to pay for.
        """
        self.session.payment_complete = True
        self.session.save()
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('payments', kwargs={'pk': 1}))
        self.assertRedirects(response, reverse(
            'dashboard', kwargs={'pk': self.user.pk}))

    def test_total_price_calculation(self):
        """
        Test that the total price is calculated correctly on the
        payment page.
        """
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('payments', kwargs={'pk': 1}))
        self.assertEqual(response.context['total_price'], Decimal('50.00'))


class PaymentCreateViewTestCases(TestCase):
    """
    Test cases for the payment create view.
    """

    def setUp(self):
        """Create a TutoringSession instance for the test cases."""

        self.user = User.objects.create_user(
            username='test_user', password='test_password'
        )

        self.tutor = Tutor.objects.create(
            user=self.user,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True
        )

        self.subject = Subject.objects.create(name='Mathematics')

        self.session = TutoringSession.objects.create(
            pk=1,
            tutor=self.tutor,
            student=self.user,
            price=Decimal('50.00'),
            payment_complete=False,
            subject=self.subject,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            created_at=timezone.now(),
            location_url='https://example.com/location',
            session_name='Math Tutoring Session',
            event_uri='event_uri_example',
            invitee_uri='invitee_uri_example',
            cancel_url='https://example.com/cancel',
            reschedule_url='https://example.com/reschedule',
        )

    def test_payment_create_status_code(self):
        """Test the status code of the payment create page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('payment_create'))
        self.assertEqual(response.status_code, 200)

    def test_payment_create_template(self):
        """Test the template used to render the payment create page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('payment_create'))
        self.assertTemplateUsed(response, 'booking/payment_create.html')

    def test_payment_create_login_required(self):
        """
        Test that the user must be logged in to access the payment
        create page.
        """
        response = self.client.get(reverse('payment_create'))
        self.assertEqual(response.status_code, 302)

    def test_payment_create_context(self):
        """Test the context of the payment create page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('payment_create'))
        self.assertEqual(
            response.context['STRIPE_PUBLIC_KEY'], settings.STRIPE_PUBLIC_KEY)

    def test_payment_create_post_request(self):
        """
        Test that a POST request to the payment create page creates a
        payment object.
        """
        self.client.login(username='test_user', password='test_password')
        response = self.client.post(reverse('payment_create'), {
            'sessions': '1',
            'user': self.user.pk,
            'amount': '50.00',
            'status': 'pending',
            'date': timezone.now(),
            'client_secret': 'client_secret_example',
            'currency': 'eur',
            'stripe_id': 'stripe_id_example',
        })
        self.assertEqual(response.status_code, 302)

    def test_payment_success_url(self):
        """
        Test that the user is redirected to the payment success page
        after creating a payment object.
        """
        self.client.login(username='test_user', password='test_password')
        response = self.client.post(reverse('payment_create'), {
            'sessions': '1',
            'user': self.user.pk,
            'amount': '50.00',
            'status': 'pending',
            'date': timezone.now(),
            'client_secret': 'client_secret_example',
            'currency': 'eur',
            'stripe_id': 'stripe_id_example',
        })
        self.assertRedirects(response, reverse(
            'payment_success', kwargs={'pk': 1}))


class PaymentDetailViewTestCases(TestCase):
    """
    Test cases for the payment detail view.
    """

    def setUp(self):
        """Create a Payment instance for the test cases."""

        self.user = User.objects.create_user(
            username='test_user', password='test_password'
        )

        self.tutor = Tutor.objects.create(
            user=self.user,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True
        )

        self.subject = Subject.objects.create(name='Mathematics')

        self.session = TutoringSession.objects.create(
            tutor=self.tutor,
            student=self.user,
            price=Decimal('50.00'),
            payment_complete=False,
            subject=self.subject,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            created_at=timezone.now(),
            location_url='https://example.com/location',
            session_name='Math Tutoring Session',
            event_uri='event_uri_example',
            invitee_uri='invitee_uri_example',
            cancel_url='https://example.com/cancel',
            reschedule_url='https://example.com/reschedule',
        )

        self.payment = Payment.objects.create(
            pk=1,
            user=self.user,
            amount=Decimal('50.00'),
            status='pending',
            date=timezone.now(),
            client_secret='client_secret_example',
            currency='eur',
            stripe_id='stripe_id_example',
        )

    def test_payment_detail_status_code(self):
        """Test the status code of the payment detail page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(
            reverse('payment_success', kwargs={'pk': self.payment.pk}))
        self.assertEqual(response.status_code, 200)

    def test_payment_detail_template(self):
        """Test the template used to render the payment detail page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(
            reverse('payment_success', kwargs={'pk': self.payment.pk}))
        self.assertTemplateUsed(response, 'booking/payment_success.html')

    def test_payment_detail_login_required(self):
        """
        Test that the user must be logged in to access the payment
        detail page.
        """
        response = self.client.get(
            reverse('payment_success', kwargs={'pk': self.payment.pk}))
        self.assertEqual(response.status_code, 302)

    def test_payment_detail_context(self):
        """Test the context of the payment detail page."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(
            reverse('payment_success', kwargs={'pk': self.payment.pk}))
        self.assertEqual(response.context['payment'], self.payment)
