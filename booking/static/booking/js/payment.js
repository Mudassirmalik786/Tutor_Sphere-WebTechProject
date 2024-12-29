const paymentData = JSON.parse(document.getElementById('payment-data').textContent);
const stripePublicKey = paymentData.stripe_public_key;
const clientSecret = paymentData.client_secret;
const sessionIds = paymentData.session_ids;
const userId = paymentData.user_id;
const cachePaymentDataUrl = paymentData.cache_payment_data_url;
const developmentString = paymentData.development;
const paymentCreateUrl = paymentData.payment_create_url;

const stripe = Stripe(stripePublicKey);

const options = {
    clientSecret: clientSecret,
    // Fully customizable with appearance API.
    appearance: {
        theme: 'flat'
    }
};

// Set up Stripe.js and Elements to use in checkout form, passing the client secret obtained in a previous step
const elements = stripe.elements(options);

// Create and mount the Payment Element
const paymentElement = elements.create('payment');
paymentElement.mount('#payment-element');

// Submit the payment to Stripe
const form = document.getElementById('payment-form');


form.addEventListener('submit', async (event) => {
    event.preventDefault();
    $('#submit').attr('disabled', true);

    const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    const postData = {
        csrfmiddlewaretoken: csrfToken,
        client_secret: options.clientSecret,
        user: userId,
        sessions: sessionIds,
    };

    const development = developmentString === 'True' ? true : false;

    if (development) {
        return_url = `http://127.0.0.1:8000${paymentCreateUrl}?user_id=${ userId }&sessions=${sessionIds}`;
    } else {
        return_url = `https://gipfel-tutor-768a610dc54f.herokuapp.com${paymentCreateUrl}?user_id=${ userId }&sessions=${sessionIds}`;
    }


    $.post(cachePaymentDataUrl, postData).done(async function () {
        const {
            error
        } = await stripe.confirmPayment({
            //`Elements` instance that was used to create the Payment Element
            elements,
            confirmParams: {
                // change this url to dynamic when deploying
                return_url: return_url,
            }
        });

        if (error) {
            // This point will only be reached if there is an immediate error when
            // confirming the payment. Show error to your customer (for example, payment
            // details incomplete)
            const messageContainer = document.querySelector('#error-message');
            messageContainer.classList.add('alert', 'alert-danger');
            messageContainer.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + error.message;
            $('#submit').attr('disabled', false);
        } else {
            // Your customer will be redirected to your `return_url`. For some payment
            // methods like iDEAL, your customer will be redirected to an intermediate
            // site first to authorize the payment, then redirected to the `return_url`.
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {});
});