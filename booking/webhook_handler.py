import time
from django.http import HttpResponse
from django.contrib import auth
from booking.models import Payment, TutoringSession
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


# -> Credit for the webhook handler class goes to Code Institute Tutorials: https://github.com/Code-Institute-Solutions/Boutique-Ado/tree/master  # noqa


class StripeWH_Handler:
    """
    Handle Stripe webhooks.

    This class is responsible for handling various webhook events received
    from Stripe.
    """

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, payment):
        """
        Send the user a confirmation email
        """
        sessions = payment.sessions.all()
        cust_email = payment.user.email
        subject = render_to_string(
            'booking/confirmation_emails/confirmation_email_subject.txt',
            {'payment': payment})
        body = render_to_string(
            'booking/confirmation_emails/confirmation_email_body.txt',
            {
                'sessions': sessions,
                'payment': payment,
                'contact_email': settings.DEFAULT_FROM_EMAIL
            }
        )
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event.

        Args:
            event (dict): The webhook event received from Stripe.

        Returns:
            HttpResponse: The response indicating the handling of the webhook
            event.
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}', status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe.

        Args:
            event (dict): The payment_intent.succeeded webhook event received
            from Stripe.

        Returns:
            HttpResponse: The response indicating the handling of the webhook
            event.
        """
        intent = event.data.object
        session_ids = intent.metadata.sessions.split(",")

        max_attempts = 3
        delay_between_attempts = 2  # seconds

        for attempt in range(max_attempts):
            try:
                payment = Payment.objects.get(
                    stripe_id=intent.id,
                )
                self._send_confirmation_email(payment)
                return HttpResponse(
                    content=(f'Webhook received: {event["type"]} | SUCCESS: '
                             f'Verified payment already in database'),
                    status=200,
                )
            except Payment.DoesNotExist:
                if attempt < max_attempts - 1:
                    time.sleep(delay_between_attempts)
                else:
                    user = auth.User.objects.get(id=intent.metadata.user_id)
                    try:
                        payment = Payment.objects.create(
                            user=user,
                            amount=intent.amount,
                            status="succeeded",
                            client_secret=intent.client_secret,
                            currency=intent.currency,
                            stripe_id=intent.id,
                        )

                        # Update the payment_complete field of the sessions
                        sessions_to_pay = TutoringSession.objects.filter(
                            pk__in=session_ids)

                        for session in sessions_to_pay:
                            session.payment_complete = True
                            session.payment = self.object
                            session.save()

                    except Exception as e:
                        if payment:
                            payment.delete()
                        return HttpResponse(
                            content=(f'Webhook received: {event["type"]} | '
                                     f'ERROR: {e}'),
                            status=500,
                        )
                    self._send_confirmation_email(payment)
                    return HttpResponse(
                        content=(f'Webhook received: {event["type"]} | '
                                 f'SUCCESS: Payment does not exist after '
                                 f'{max_attempts} attempts - created new '
                                 f'payment in database'),
                        status=200,
                    )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe.

        Args:
            event (dict): The payment_intent.payment_failed webhook event
                received from Stripe.

        Returns:
            HttpResponse: The response indicating the handling of the webhook
                event.
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}', status=200
        )
