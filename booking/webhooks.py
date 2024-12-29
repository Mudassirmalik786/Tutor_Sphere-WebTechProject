import json
import os
import stripe
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from booking.webhook_handler import StripeWH_Handler
from gipfel_tutor import settings

# -> Credit for the webhook handling: https://docs.stripe.com/webhooks/quickstart  # noqa

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@csrf_exempt
def webhook(request):
    """
    Handle incoming webhook events from Stripe.

    Args:
        request (HttpRequest): The incoming HTTP request object.

    Returns:
        JsonResponse: The JSON response indicating the success or failure of
            the webhook event handling.
    """
    event = None

    try:
        event = json.loads(request.body)
    except json.decoder.JSONDecodeError as e:
        return JsonResponse({'success': False}, status=400)

    if endpoint_secret:
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                request.body, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({'success': False}, status=400)

    handler = StripeWH_Handler(request)

    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,  # noqa
    }

    event_type = event['type']

    event_handler = event_map.get(event_type, handler.handle_event)

    response = event_handler(event)
    return response
