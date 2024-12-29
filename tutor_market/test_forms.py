from django.test import TestCase
from tutor_market.forms import RatingForm, TutorForm
from tutor_market.models import Tutor, Subject, Value
from django.contrib.auth.models import User
from decimal import Decimal


class TutorFormTestCases(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(name='Math')
        self.value = Value.objects.create(name='Patience')

    def test_valid_form(self):
        form_data = {
            'display_name': 'Test Tutor',
            'subjects': [self.subject.id],
            'hourly_rate': Decimal('50.00'),
            'values': [self.value.id],
            'catch_phrase': 'Learn with the best!',
            'description': 'Experienced tutor in various subjects.',
            'profile_image': None,  # Assuming no file upload in this test
            'iban': 'DE02500105170137075030',
            'calendly_event_url': 'https://calendly.com/test-tutor',
        }
        form = TutorForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

    def test_invalid_form_url(self):
        form_data = {
            'display_name': 'Test Tutor',
            'subjects': [self.subject.id],
            'hourly_rate': Decimal('50.00'),
            'values': [self.value.id],
            'catch_phrase': 'Learn with the best!',
            'description': 'Experienced tutor in various subjects.',
            'profile_image': None,  # Assuming no file upload in this test
            'iban': 'DE02500105170137075030',
            'calendly_event_url': 'invalid-url',
        }
        form = TutorForm(data=form_data)
        self.assertFalse(
            form.is_valid(), msg="Form should be invalid with an invalid URL.")


class RatingFormTestCases(TestCase):

    def test_valid_form(self):
        form_data = {
            'score': 5,
            'comment': 'Great tutor!',
        }
        form = RatingForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

    def test_invalid_form_score(self):
        form_data = {
            'score': 6,
            'comment': 'Great tutor!',
        }
        form = RatingForm(data=form_data)
        self.assertFalse(
            form.is_valid(), msg="Form should be invalid with a score greater "
            "than 5.")
