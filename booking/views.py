from decimal import Decimal
import json
from typing import Any
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import requests
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from booking.forms import CalendlyUriForm, CancelForm, PaymentForm
from booking.models import Payment, TutoringSession
from gipfel_tutor import settings
from tutor_market.models import Tutor
import stripe
from datetime import datetime


@require_POST
def cache_payment_data(request):
    """
    Cache payment data and modify Stripe PaymentIntent metadata.

    This function is responsible for caching payment data and modifying the
    metadata of a Stripe PaymentIntent.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        Exception: If an error occurs while processing the payment.

    """
    try:
        payment_intent_id = request.POST.get(
            'client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session_id_string = request.POST.get('sessions')
        user_id = request.POST.get('user')
        stripe.PaymentIntent.modify(payment_intent_id, metadata={
            'user_id': user_id,
            'sessions': session_id_string,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.warning(
            request, 'An error occurred while processing your payment.')
        return HttpResponse(content=e, status=400)


def _get_json_from_calendly_uri(uri, tutor, request):
    """
    Retrieves JSON data from the specified Calendly URI.

    Args:
        uri (str): The Calendly URI to retrieve JSON data from.
        tutor (Tutor): The tutor object associated with the Calendly access
            token.
        request (HttpRequest): The HTTP request object (optional).

    Returns:
        Response: The response object containing the JSON data.

    Raises:
        None

    """
    calendly_access_token = tutor.calendly_access_token
    headers = {'Authorization': f'Bearer {calendly_access_token}'}
    response = requests.get(uri, headers=headers)
    if response.status_code == 200:
        return response
    else:
        if request:
            messages.warning(
                request, f'''An error occurred while loading the event data.
                {response}'''
            )
        return response


def _write_calendly_data_to_db(event_data, invitee_data, tutor, student, request):  # noqa
    """
    Writes Calendly data to the database and creates a new tutoring session.

    Args:
        event_data (dict): The event data received from Calendly.
        invitee_data (dict): The invitee data received from Calendly.
        tutor (Tutor): The tutor object associated with the session.
        student (Student): The student object associated with the session.
        request (HttpRequest): The HTTP request object.

    Returns:
        TutoringSession: The created tutoring session object.

    Raises:
        KeyError: If the join URL is not found in the event data.

    """
    questions_and_answers = ''
    if invitee_data['resource']['questions_and_answers']:
        i_data = invitee_data['resource']['questions_and_answers'][0]['answer']
        questions_and_answers = i_data

    join_url = ''
    try:
        join_url = event_data['resource']['location']['join_url']
    except KeyError:
        messages.warning(
            request, 'Ask your tutor to provide a join link for the session.')

    session = TutoringSession.objects.create(
        tutor=tutor,
        student=student,
        price=tutor.hourly_rate,
        subject=tutor.subjects.first(),

        # Calendly json fields
        start_time=event_data['resource']['start_time'],
        end_time=event_data['resource']['end_time'],
        created_at=event_data['resource']['created_at'],
        location_url=join_url,
        session_name=event_data['resource']['name'],
        event_uri=event_data['resource']['uri'],
        invitee_uri=invitee_data['resource']['uri'],
        cancel_url=invitee_data['resource']['cancel_url'],
        reschedule_url=invitee_data['resource']['reschedule_url'],
        invitee_email=invitee_data['resource']['email'],
        invitee_notes=questions_and_answers
    )
    session.save()
    messages.success(request, 'Session created successfully.')
    return session


@login_required
@require_POST
def fetch_calendly_data_view(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View for fetching and displaying the tutor's Calendly data.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the tutor.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        Http404: If the tutor with the given primary key does not exist.
    """
    tutor = get_object_or_404(Tutor, pk=pk)
    student = request.user

    form = CalendlyUriForm(request.POST)
    if not form.is_valid():
        messages.warning(request, 'Invalid Calendly form data.')
        return redirect('tutor_detail', pk=pk)

    # get the uris
    event_uri = form.cleaned_data['event_uri']
    invitee_uri = form.cleaned_data['invitee_uri']

    # get the data from the uris using the calendly api2
    event_data_response = _get_json_from_calendly_uri(
        event_uri, tutor, request)
    invitee_data_response = _get_json_from_calendly_uri(
        invitee_uri, tutor, request)

    if (event_data_response.status_code != 200 or
            invitee_data_response.status_code != 200):
        messages.warning(request, '''Something went wrong while fetching the
                         data from Calendly.''')
        return redirect('tutor_detail', pk=pk)

    event_data = event_data_response.json()
    invitee_data = invitee_data_response.json()

    session = _write_calendly_data_to_db(
        event_data, invitee_data, tutor, student, request)

    return redirect('schedule_success', pk=session.pk)


def cancel_session_view(request, pk):
    """
    View for cancelling a tutoring session.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the tutoring session to be cancelled.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        Http404: If the tutoring session with the given primary key does not
            exist.
    """
    session = get_object_or_404(TutoringSession, pk=pk)
    tutor = session.tutor
    student = session.student

    if not (request.user == student or request.user == tutor.user):
        messages.warning(
            request, 'You are not authorized to cancel this session.')
        return redirect('dashboard', pk=request.user.id)

    if (session.session_status == 'cancelled'
            or session.session_status == 'completed'):
        messages.warning(
            request, 'This session has already been cancelled or completed.')
        return redirect('dashboard', pk=request.user.id)

    if request.method == 'POST':
        form = CancelForm(request.POST)
        if not form.is_valid():
            messages.warning(request, 'Invalid form data.')
            return redirect('cancel_session', pk=pk)

        url = f"{session.event_uri}/cancellation"

        reason = 'No reason given'
        if form.cleaned_data['cancel_reason']:
            reason = form.cleaned_data['cancel_reason']
        canceled_by = request.user.email
        created_at = datetime.now().isoformat()

        payload = {
            "reason": reason,
            "canceled_by":  canceled_by,
            "created_at": created_at,
        }
        calendly_access_token = tutor.calendly_access_token
        headers = {'Authorization': f'Bearer {calendly_access_token}'}

        response = requests.request("POST", url, json=payload, headers=headers)

        import json  # Ensure this import is at the top of your file

        response_data = json.loads(response.text)

        if response.status_code == 201:
            messages.success(request, 'Session cancelled successfully.')
            # update the session status
            session.session_status = 'cancelled'
            session.save()

        else:
            messages.warning(request, f'''{response_data["title"]}:
                             {response_data["message"]}''')

        return redirect('dashboard', pk=request.user.pk)

    form = CancelForm()

    context = {
        'session': session,
        'form': form,
    }

    return render(request, 'booking/cancel_session.html', context)


class ScheduleSuccessView(LoginRequiredMixin, DetailView):
    """
    A view that displays the success page after scheduling a tutoring session.

    Attributes:
        model (Model): The model class to use for retrieving the tutoring
            session.
        template_name (str): The name of the template to use for rendering
            the view.
        context_object_name (str): The name of the variable to use for the
            tutoring session object in the template context.
    """
    model = TutoringSession
    template_name = 'booking/schedule_success.html'
    context_object_name = 'session'


@login_required
def payment_view(request, pk):
    """
    View for handling the payment of a tutoring session.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the user. (not used at the moment)

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        None

    """
    sessions_to_pay = TutoringSession.objects.filter(
        student=request.user, payment_complete=False)

    if not sessions_to_pay:
        messages.warning(request, 'No sessions to pay for.')
        return redirect('dashboard', pk=request.user.pk)

    total_price = round(sum([session.price for session in sessions_to_pay]))
    total_price_in_cents = total_price * 100

    # -> Credit for Stripe integration: https://stripe.com/docs/payments/accept-a-payment  # noqa
    STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.create(
        amount=total_price_in_cents,
        currency=settings.STRIPE_CURRENCY,
    )
    CLIENT_SECRET = intent.client_secret
    development = 'True' if settings.DEVELOPMENT else 'False'
    session_ids = ','.join([str(session.id) for session in sessions_to_pay])

    context = {
        'sessions': sessions_to_pay,
        'session_ids': session_ids,
        # -> Credit for quantize: https://docs.python.org/3/library/decimal.html  # noqa
        'total_price': Decimal(total_price).quantize(Decimal('0.01')),
        'STRIPE_PUBLIC_KEY': STRIPE_PUBLIC_KEY,
        'CLIENT_SECRET': CLIENT_SECRET,
        'development': development,
    }
    return render(request, 'booking/payment.html', context)


class PaymentCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a payment.

    Inherits from LoginRequiredMixin and CreateView.
    """

    model = Payment
    form_class = PaymentForm
    template_name = 'booking/payment_create.html'
    success_message = 'Payment successful.'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
        Returns the context data for the view.

        Overrides the get_context_data method of CreateView.
        Adds the STRIPE_PUBLIC_KEY to the context.
        """
        context = super().get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """
        Handles the form submission when it is valid.

        Overrides the form_valid method of CreateView.
        Converts the amount from cents to euros.
        Populates the payment model with the paid for sessions.
        Updates the sessions after the payment model is created.
        """
        # -> Credit for Decimal conversion: https://stackoverflow.com/questions/316238/python-float-to-decimal-conversion  # noqa
        amount_in_euros = Decimal(
            form.cleaned_data['amount']) / Decimal('100.00')
        form.instance.amount = amount_in_euros

        response = super().form_valid(form)

        session_ids = form.cleaned_data['sessions'].split(',')
        sessions_to_pay = TutoringSession.objects.filter(pk__in=session_ids)

        for session in sessions_to_pay:
            session.payment_complete = True
            session.payment = self.object
            session.save()

        return response

    def get_success_url(self) -> str:
        """
        Returns the URL to redirect to after a successful form submission.

        Overrides the get_success_url method of CreateView.
        """
        return reverse('payment_success', kwargs={'pk': self.object.pk})


class PaymentDetailView(LoginRequiredMixin, DetailView):
    """
    A view that displays the details of a payment.

    Inherits from LoginRequiredMixin and DetailView.
    """

    model = Payment
    template_name = 'booking/payment_success.html'
    context_object_name = 'payment'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Adds additional context data to be used in the template.

        Additional Context:
            sessions (QuerySet): The tutoring sessions associated with the
                payment.

        Returns:
            A dictionary containing the context data.
        """
        context = super().get_context_data(**kwargs)
        context['sessions'] = TutoringSession.objects.filter(
            payment=self.object)
        return context
