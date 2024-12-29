/**
 * Fills out the payment form with the provided paymentIntent data and submits the form.
 * @param {Object} paymentIntent - The paymentIntent object containing the payment details.
 */
function fillOutForm(paymentIntent) {
    const user_id = new URLSearchParams(window.location.search).get('user_id');
    const sessions = new URLSearchParams(window.location.search).get('sessions');
    const form = $('#payment-form');

    // -> Credit for setting form values: https://www.w3schools.com/jsref/dom_obj_form.asp
    form.find('[name="user"]').val(user_id);
    form.find('[name="amount"]').val(paymentIntent.amount);
    form.find('[name="status"]').val(paymentIntent.status);
    form.find('[name="client_secret"]').val(paymentIntent.client_secret);
    form.find('[name="currency"]').val(paymentIntent.currency);
    form.find('[name="stripe_id"]').val(paymentIntent.id);
    form.find('[name="sessions"]').val(sessions);

    form.submit();
}

// Initialize Stripe.js using your publishable key
const STRIPE_PUBLIC_KEY = JSON.parse(document.getElementById('stripe-public-key').textContent);
const stripe = Stripe(STRIPE_PUBLIC_KEY);

// Retrieve the "payment_intent_client_secret" query parameter appended to
// your return_url by Stripe.js
const clientSecret = new URLSearchParams(window.location.search).get('payment_intent_client_secret');

// Retrieve the PaymentIntent
stripe.retrievePaymentIntent(clientSecret).then(({
    paymentIntent
}) => {
    const message = document.querySelector('#message');

    // Inspect the PaymentIntent `status` to indicate the status of the payment
    // to your customer.
    //
    // Some payment methods will [immediately succeed or fail][0] upon
    // confirmation, while others will first enter a `processing` state.
    //
    // [0]: https://stripe.com/docs/payments/payment-methods#payment-notification
    switch (paymentIntent.status) {
        case 'succeeded':
            message.innerText = 'Success! Payment received.';
            fillOutForm(paymentIntent);
            break;

        case 'processing':
            message.innerText = "Payment processing. We'll update you when payment is received.";
            fillOutForm(paymentIntent);
            break;

        case 'requires_payment_method':
            message.innerText = 'Payment failed. Please try another payment method.';
            // Redirect your user back to your payment page to attempt collecting
            // payment again
            break;

        default:
            message.innerText = 'Something went wrong.';
            break;
    }
});