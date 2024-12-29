from django.test import TestCase
from django.contrib.auth.models import User
from booking.models import Payment
from .forms import CalendlyUriForm, PaymentForm, CancelForm


class CalendlyUriFormTestCase(TestCase):
    """
    Test Case for the CalendlyUriForm form.
    """

    def test_form_valid(self):
        """
        Test the form with valid data.
        """
        form = CalendlyUriForm(data={
            'event_uri': 'https://calendly.com/event',
            'invitee_uri': 'https://calendly.com/invitee'
        })
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

    def test_form_invalid(self):
        """
        Test the form with invalid data.
        """
        form = CalendlyUriForm(data={})
        self.assertFalse(
            form.is_valid(), msg="Form should be invalid with no data.")


class PaymentFormTestCase(TestCase):
    """
    Test Case for the PaymentForm form.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password'
        )

    def test_form_valid(self):
        """
        Test the form with valid data.
        """
        form_data = {
            'user': self.user,
            'amount': 10.00,
            'status': 'pending',
            'date': '2022-01-01 00:00:00',
            'client_secret': 'test_secret',
            'currency': 'eur',
            'stripe_id': 'test_id'
        }
        form = PaymentForm(form_data)
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

    def test_form_invalid(self):
        """
        Test the form with invalid data.
        """
        form = PaymentForm(data={})
        self.assertFalse(
            form.is_valid(), msg="Form should be invalid with no data.")


class CancelFormTestCase(TestCase):
    """
    Test Case for the CancelForm form.
    """

    def test_form_valid(self):
        """
        Test the form with valid data.
        """
        form = CancelForm(data={'cancel_reason': 'Test reason'})
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

        form2 = CancelForm(data={})
        self.assertTrue(form.is_valid(), msg=form2.errors.as_text())

    def test_form_invalid(self):
        """
        Test the form with invalid data.
        """
        form = CancelForm(data={'cancel_reason': 'A' * 201})
        self.assertFalse(
            form.is_valid(), msg="Form should be invalid with too long a "
            "reason.")
