from django.utils import timezone
from booking.models import Payment, TutoringSession
from tutor_market.models import Tutor, Subject, Value
from django.test import TestCase, Client
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages

from booking.forms import CalendlyUriForm
from tutor_market.forms import RatingForm
from tutor_market.models import Rating, Subject, Tutor, Value
from tutor_market.views import TutorCreateView


class TutorListViewTestCases(TestCase):
    """Test cases for the TutorListView view."""

    def setUp(self):
        """Set up the test case."""
        self.user1 = User.objects.create_user(
            username='test_user', password='test_password'
        )

        self.user2 = User.objects.create_user(
            username='test_user2', password='test_password'
        )

        self.tutor1 = Tutor.objects.create(
            user=self.user1,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True
        )

        self.tutor2 = Tutor.objects.create(
            user=self.user2,
            display_name='Test Tutor 2',
            hourly_rate=Decimal('40.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=False
        )

        self.subject = Subject.objects.create(name='Math')

        self.value = Value.objects.create(name='Patience')

        self.review = Rating.objects.create(
            tutor=self.tutor1,
            user=self.user2,
            score=5,
            comment='Great tutor!'
        )

    def test_tutor_list_view_status_code(self):
        """Test the status code of the TutorListView view."""
        response = self.client.get(reverse('tutor_list'))
        self.assertEqual(response.status_code, 200)

    def test_tutor_list_view_template(self):
        """Test the template used by the TutorListView view."""
        response = self.client.get(reverse('tutor_list'))
        self.assertTemplateUsed(response, 'tutor_market/tutor_list.html')

    def test_tutor_list_view_context(self):
        """Test the context of the TutorListView view."""
        response = self.client.get(reverse('tutor_list'))
        self.assertEqual(len(response.context['tutor_list']), 2)
        self.assertEqual(response.context['tutor_list'][1], self.tutor2)

    def test_tutor_list_view_subject_filter(self):
        """Test the subject filter of the TutorListView view."""
        self.tutor1.subjects.add(self.subject.id)
        response = self.client.get(
            reverse('tutor_list'), {'subject': self.subject.name})
        self.assertEqual(len(response.context['tutor_list']), 1)
        self.assertEqual(response.context['tutor_list'][0], self.tutor1)

    def test_tutor_list_view_teachingvalue_filter(self):
        """Test the teaching value filter of the TutorListView view."""
        self.tutor1.values.add(self.value.id)
        response = self.client.get(
            reverse('tutor_list'), {'teachingvalue': self.value.name})
        self.assertEqual(len(response.context['tutor_list']), 1)
        self.assertEqual(response.context['tutor_list'][0], self.tutor1)

    def test_tutor_list_view_query_filter(self):
        """Test the query filter of the TutorListView view."""
        response = self.client.get(
            reverse('tutor_list'), {'q': 'Test Tutor 2'})
        self.assertEqual(len(response.context['tutor_list']), 1)
        self.assertEqual(response.context['tutor_list'][0], self.tutor2)

    def test_tutor_list_view_name_sorting(self):
        """Test the sorting of the TutorListView view by name."""
        response = self.client.get(reverse('tutor_list'), {'sorting': 'name'})
        self.assertEqual(response.context['tutor_list'][0], self.tutor1)
        self.assertEqual(response.context['tutor_list'][1], self.tutor2)

    def test_tutor_list_view_cheapest_sorting(self):
        """Test the sorting of the TutorListView view by hourly rate."""
        response = self.client.get(
            reverse('tutor_list'), {'sorting': 'cheapest'})
        self.assertEqual(response.context['tutor_list'][0], self.tutor2)
        self.assertEqual(response.context['tutor_list'][1], self.tutor1)

    def test_tutor_list_view_highest_rated_sorting(self):
        """Test the sorting of the TutorListView view by highest rated."""
        response = self.client.get(
            reverse('tutor_list'), {'sorting': 'highest_rated'})
        self.assertEqual(response.context['tutor_list'][0], self.tutor1)
        self.assertEqual(response.context['tutor_list'][1], self.tutor2)

    def test_tutor_list_view_most_reviews_sorting(self):
        """Test the sorting of the TutorListView view by most reviews."""
        response = self.client.get(
            reverse('tutor_list'), {'sorting': 'most_reviews'})
        self.assertEqual(response.context['tutor_list'][0], self.tutor1)
        self.assertEqual(response.context['tutor_list'][1], self.tutor2)

    def test_tutor_list_view_most_expensive_sorting(self):
        """Test the sorting of the TutorListView view by most expensive."""
        response = self.client.get(
            reverse('tutor_list'), {'sorting': 'most_expensive'})
        self.assertEqual(response.context['tutor_list'][0], self.tutor1)
        self.assertEqual(response.context['tutor_list'][1], self.tutor2)


class TutorDetailViewTestCases(TestCase):
    """Test cases for the TutorDetailView view."""

    def setUp(self):
        """Set up the test case."""
        self.user1 = User.objects.create_user(
            username='test_user', password='test_password'
        )

        self.user2 = User.objects.create_user(
            username='test_user2', password='test_password'
        )

        self.tutor1 = Tutor.objects.create(
            user=self.user1,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True
        )

        self.tutor2 = Tutor.objects.create(
            user=self.user2,
            display_name='Test Tutor 2',
            hourly_rate=Decimal('40.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=False
        )

        self.subject = Subject.objects.create(name='Math')

        self.value = Value.objects.create(name='Patience')

        self.review = Rating.objects.create(
            tutor=self.tutor1,
            user=self.user2,
            score=5,
            comment='Great tutor!'
        )

    def test_tutor_detail_view_status_code(self):
        """Test the status code of the TutorDetailView view."""
        response = self.client.get(
            reverse('tutor_detail', args=[self.tutor1.id]))
        self.assertEqual(response.status_code, 200)

    def test_tutor_detail_view_template(self):
        """Test the template used by the TutorDetailView view."""
        response = self.client.get(
            reverse('tutor_detail', args=[self.tutor1.id]))
        self.assertTemplateUsed(response, 'tutor_market/tutor_detail.html')

    def test_tutor_detail_view_context(self):
        """Test the context of the TutorDetailView view."""
        response = self.client.get(
            reverse('tutor_detail', args=[self.tutor1.id]))
        self.assertEqual(response.context['tutor'], self.tutor1)
        self.assertIsInstance(response.context['form'], RatingForm)
        self.assertIsInstance(
            response.context['calendly_form'], CalendlyUriForm)
        self.assertEqual(response.context['review_counts'][5]['count'], 1)
        self.assertFalse(response.context['existing_review'])
        self.assertIsNone(response.context['upcoming_sessions'])

    def test_tutor_detail_view_user_unauthenticated(self):
        """Test the TutorDetailView view with an unauthenticated user."""
        self.client.logout()
        response = self.client.get(
            reverse('tutor_detail', args=[self.tutor1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['existing_review'])
        self.assertIsNone(response.context['upcoming_sessions'])

    def test_post_review_not_authenticated(self):
        """Test that a user must be logged in to leave a review."""
        response = self.client.post(
            reverse('tutor_detail', args=[self.tutor1.id]), {
                'score': 5,
                'comment': 'Great tutor!'
            })
        self.assertRedirects(response, reverse(
            'tutor_detail', args=[self.tutor1.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), 'You must be logged in to leave a review.')

    def test_post_review_own_profile(self):
        """Test that a user cannot leave a review on their own profile."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.post(
            reverse('tutor_detail', args=[self.tutor1.id]), {
                'score': 5,
                'comment': 'Great tutor!'
            })
        self.assertRedirects(response, reverse(
            'tutor_detail', args=[self.tutor1.id]))

        # -> Credit for testing for django messages: https://stackoverflow.com/a/57998247  # noqa
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[2]), 'You cannot leave a review on your own profile.')

    def test_post_review_invalid_form(self):
        """Test that an invalid form submission shows a warning message."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.post(
            reverse('tutor_detail', args=[self.tutor2.id]), {
                'score': '',
                'comment': 'Great tutor!'
            })
        self.assertRedirects(response, reverse(
            'tutor_detail', args=[self.tutor2.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[2]),
                         'Form was not valid. Please try again.')


class TutorCreateViewTestCases(TestCase):
    """
    Test cases for the TutorCreateView.
    """

    def setUp(self):
        """Create a user for the test cases."""
        self.user = User.objects.create_user(
            username='test_user', password='test_password'
        )
        self.subject = Subject.objects.create(name='Math')
        self.value = Value.objects.create(name='Patience')

    def test_tutor_create_view_success(self):
        """Test that the view creates a new tutor profile successfully."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('add_tutor'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_market/add_tutor.html')

        form_data = {
            'display_name': 'Test Tutor',
            'hourly_rate': 50.00,
            'catch_phrase': 'Learn with the best!',
            'description': 'Experienced tutor in various subjects.',
            'subjects': [self.subject.id],
            'values': [self.value.id],
        }
        response = self.client.post(reverse('add_tutor'), data=form_data)
        self.assertRedirects(response, reverse(
            'dashboard', kwargs={'pk': self.user.pk}))

        tutor = Tutor.objects.get(user=self.user)
        self.assertEqual(tutor.display_name, 'Test Tutor')
        self.assertEqual(tutor.hourly_rate, 50.00)

    def test_tutor_create_view_form_invalid(self):
        """Test that the view handles invalid form data."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('add_tutor'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_market/add_tutor.html')

        form_data = {
            'display_name': 'Test Tutor',
            'hourly_rate': 'invalid',
            'catch_phrase': 'Learn with the best!',
            'description': 'Experienced tutor in various subjects.',
            'subjects': [self.subject.id],
            'values': [self.value.id],
        }
        response = self.client.post(reverse('add_tutor'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_market/add_tutor.html')

        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('hourly_rate', form.errors)
        self.assertEqual(form.errors['hourly_rate'], ['Enter a number.'])


class TutorUpdateViewTestCases(TestCase):
    """
    Test cases for the TutorUpdateView.
    """

    def setUp(self):
        """Create users and a tutor profile for the test cases."""
        self.user = User.objects.create_user(
            username='test_user', password='test_password')
        self.user2 = User.objects.create_user(
            username='user2', password='other_password')
        self.subject = Subject.objects.create(name='Math')
        self.value = Value.objects.create(name='Patience')
        self.tutor = Tutor.objects.create(
            user=self.user,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True
        )

    def test_update_view_owner(self):
        """Test that the owner can access the update view."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('edit_tutor', args=[self.tutor.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_market/edit_tutor.html')

    def test_update_view_not_owner(self):
        """Test that a non-owner cannot access the update view."""
        self.client.login(username='user2', password='other_password')
        response = self.client.get(reverse('edit_tutor', args=[self.tutor.id]))
        self.assertEqual(response.status_code, 403)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), ('You do not have permission to update this '
                               'profile.')
        )

    def test_update_view_form_valid(self):
        """Test that the update view handles valid form data."""
        self.client.login(username='test_user', password='test_password')
        form_data = {
            'display_name': 'Updated Tutor',
            'hourly_rate': 60.00,
            'catch_phrase': 'Learn with the best!',
            'description': 'Updated description.',
            'subjects': [self.subject.id],
            'values': [self.value.id],
        }
        response = self.client.post(
            reverse('edit_tutor', args=[self.tutor.id]), data=form_data)
        self.assertRedirects(response, reverse(
            'dashboard', kwargs={'pk': self.user.pk}))
        self.tutor.refresh_from_db()
        self.assertEqual(self.tutor.display_name, 'Updated Tutor')
        self.assertEqual(self.tutor.hourly_rate, Decimal('60.00'))

    def test_update_view_form_invalid(self):
        """Test that the update view handles invalid form data."""
        self.client.login(username='test_user', password='test_password')
        form_data = {
            'display_name': 'Updated Tutor',
            'hourly_rate': 'invalid',
            'catch_phrase': 'Learn with the best!',
            'description': 'Updated description.',
            'subjects': [self.subject.id],
            'values': [self.value.id],
        }
        response = self.client.post(
            reverse('edit_tutor', args=[self.tutor.id]), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_market/edit_tutor.html')
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('hourly_rate', form.errors)
        self.assertEqual(form.errors['hourly_rate'], [
                         'Enter a number.'])


class TutorDeleteViewTestCases(TestCase):
    """
    Test cases for the TutorDeleteView.
    """

    def setUp(self):
        """Create users and a tutor profile for the test cases."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_user', password='test_password')
        self.user2 = User.objects.create_user(
            username='user2', password='other_password')
        self.tutor = Tutor.objects.create(
            user=self.user,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True
        )

    def test_delete_view_owner(self):
        """Test that the owner can access the delete view."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(
            reverse('delete_tutor', args=[self.tutor.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'tutor_market/tutor_confirm_delete.html')

    def test_delete_view_not_owner(self):
        """Test that a non-owner cannot access the delete view."""
        self.client.login(username='user2', password='other_password')
        response = self.client.get(
            reverse('delete_tutor', args=[self.tutor.id]))
        self.assertEqual(response.status_code, 403)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), ('You do not have permission to delete this '
                               'profile.')
        )

    def test_delete_view_success(self):
        """Test that the owner can delete the tutor profile."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.post(
            reverse('delete_tutor', args=[self.tutor.id]))
        self.assertRedirects(response, reverse('tutor_list'))
        self.assertFalse(Tutor.objects.filter(id=self.tutor.id).exists())


class DashboardViewTestCases(TestCase):
    """
    Test cases for the dashboard views.
    """

    def setUp(self):
        """Create users, tutor profiles, and sessions for the test cases."""
        self.student_user = User.objects.create_user(
            username='student_user', password='student_password')
        self.tutor_user = User.objects.create_user(
            username='tutor_user', password='tutor_password')
        self.tutor = Tutor.objects.create(
            user=self.tutor_user,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True,
            calendly_access_token='valid_token',
            calendly_event_url='https://calendly.com/test_event'
        )
        self.subject = Subject.objects.create(name='Math')
        self.session = TutoringSession.objects.create(
            tutor=self.tutor,
            student=self.student_user,
            price=Decimal('50.00'),
            payment_complete=False,
            subject=self.subject,
            start_time=timezone.now() + timezone.timedelta(days=1),
            end_time=timezone.now() + timezone.timedelta(days=1, hours=1),
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
        self.payment = Payment.objects.create(
            user=self.student_user,
            amount=Decimal('50.00'),
            date=timezone.now(),
            status='completed'
        )

    def test_dashboard_view_student(self):
        """Test that the student dashboard view works correctly."""
        self.client.login(username='student_user', password='student_password')
        response = self.client.get(
            reverse('dashboard', args=[self.student_user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'tutor_market/student_dashboard.html')
        context = response.context
        self.assertIn('upcoming_sessions', context)
        self.assertIn('booking_history', context)
        self.assertIn('payment_history', context)
        self.assertIn('amount_of_unpaid_sessions', context)

    def test_dashboard_view_tutor(self):
        """Test that the tutor dashboard view works correctly."""
        self.client.login(username='tutor_user', password='tutor_password')
        response = self.client.get(
            reverse('dashboard', args=[self.tutor_user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_market/tutor_dashboard.html')
        context = response.context
        self.assertIn('booking_history', context)
        self.assertIn('pending_sessions', context)
        self.assertIn('upcoming_sessions', context)
        self.assertIn('users_and_sessions', context)
        self.assertIn('tutor', context)

    def test_dashboard_view_access_control(self):
        """Test that a user cannot access another user's dashboard."""
        self.client.login(username='student_user', password='student_password')
        response = self.client.get(
            reverse('dashboard', args=[self.tutor_user.pk]))
        self.assertRedirects(response, reverse(
            'dashboard', args=[self.student_user.pk]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(
            messages[0]), ('You do not have permission to view this dashboard.'
                           ' We redirected you to your own dashboard.')
        )

    def test_tutor_profile_status_update(self):
        """Test that the tutor's profile status is updated correctly."""
        self.client.login(username='tutor_user', password='tutor_password')
        self.tutor.calendly_access_token = ''
        self.tutor.calendly_event_url = ''
        self.tutor.save()
        response = self.client.get(
            reverse('dashboard', args=[self.tutor_user.pk]))
        self.tutor.refresh_from_db()
        self.assertFalse(self.tutor.profile_status)
        self.assertEqual(response.status_code, 200)


class UpdateSessionStatusViewTestCases(TestCase):
    """
    Test cases for the update_session_status view.
    """

    def setUp(self):
        """Create users, tutor profiles, and sessions for the test cases."""
        self.tutor_user = User.objects.create_user(
            username='tutor_user', password='tutor_password')
        self.user2 = User.objects.create_user(
            username='user2', password='other_password')
        self.tutor = Tutor.objects.create(
            user=self.tutor_user,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True
        )
        self.subject = Subject.objects.create(name='Math')
        self.session = TutoringSession.objects.create(
            tutor=self.tutor,
            student=self.user2,
            price=Decimal('50.00'),
            payment_complete=False,
            subject=self.subject,
            start_time=timezone.now() + timezone.timedelta(days=1),
            end_time=timezone.now() + timezone.timedelta(days=1, hours=1),
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

    def test_update_session_status_owner(self):
        """Test that the tutor can update the session status."""
        self.client.login(username='tutor_user', password='tutor_password')
        response = self.client.post(
            reverse('update_session_status', args=[self.session.pk]), {
                'status': 'completed'
            })
        self.assertRedirects(response, reverse(
            'dashboard', args=[self.tutor_user.pk]))
        self.session.refresh_from_db()
        self.assertEqual(self.session.session_status, 'completed')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]),
                         'Session status updated successfully.')

    def test_update_session_status_not_owner(self):
        """Test that a non-owner cannot update the session status."""
        self.client.login(username='user2', password='other_password')
        response = self.client.post(
            reverse('update_session_status', args=[self.session.pk]), {
                'status': 'completed'
            })
        self.session.refresh_from_db()
        self.assertEqual(self.session.session_status, 'scheduled')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), ('You do not have permission to update this '
                               'session.')
        )

    def test_update_session_status_invalid_session(self):
        """Test that a 404 error is raised if the session does not exist."""
        self.client.login(username='tutor_user', password='tutor_password')
        response = self.client.post(
            reverse('update_session_status', args=[999]), {
                'status': 'completed'
            })
        self.assertEqual(response.status_code, 404)


class CalendlyInformationViewTestCases(TestCase):
    """
    Test cases for the CalendlyInformationView.
    """

    def setUp(self):
        """Create a user and a tutor profile for the test cases."""
        self.user = User.objects.create_user(
            username='test_user', password='test_password')
        self.tutor = Tutor.objects.create(
            user=self.user,
            display_name='Test Tutor',
            hourly_rate=Decimal('50.00'),
            catch_phrase='Learn with the best!',
            description='Experienced tutor in various subjects.',
            profile_status=True,
            testing_profile=True,
            calendly_access_token='valid_token',
            calendly_event_url='https://calendly.com/test_event'
        )
        self.client.login(username='test_user', password='test_password')

    def test_calendly_information_view_accessible(self):
        """Test that the Calendly information view is accessible."""
        response = self.client.get(reverse('calendly_information'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'tutor_market/calendly_information.html')

    def test_calendly_information_view_unauthenticated(self):
        """Test that the view redirects an unauthenticated user."""
        self.client.logout()
        response = self.client.get(reverse('calendly_information'))
        self.assertRedirects(
            response,
            '/accounts/login/?next=/tutor-market/calendly-information/')
