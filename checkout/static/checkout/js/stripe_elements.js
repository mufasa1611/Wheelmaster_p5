/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

/*
 * Test Card Numbers for Stripe:
 * Success: 4242 4242 4242 4242
 * Requires Auth: 4000 0025 0000 3155
 * Decline: 4000 0000 0000 0002
 * Insufficient Funds: 4000 0000 0000 9995
 */

var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
var card = elements.create('card', {style: style});
var isProcessing = false;
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fa-solid fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

function showError(message) {
    var errorDiv = document.getElementById('card-errors');
    var html = `
        <span class="icon" role="alert">
            <i class="fa-solid fa-times"></i>
        </span>
        <span>${message}</span>
    `;
    $(errorDiv).html(html);
}

function resetForm() {
    card.update({ 'disabled': false});
    $('#submit-button').attr('disabled', false);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);
    isProcessing = false;
}

// Handle form submit
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    
    if (isProcessing) return;
    
    // Gather additional form data for more comprehensive payment intent
    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);
    isProcessing = true;

    // Prepare detailed payment method and shipping information
    var paymentData = {
        payment_method: {
            card: card,
            billing_details: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                email: $.trim(form.email.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    state: $.trim(form.county.value),
                    postal_code: $.trim(form.postcode.value)
                }
            }
        },
        shipping: {
            name: $.trim(form.full_name.value),
            phone: $.trim(form.phone_number.value),
            address: {
                line1: $.trim(form.street_address1.value),
                line2: $.trim(form.street_address2.value),
                city: $.trim(form.town_or_city.value),
                country: $.trim(form.country.value),
                postal_code: $.trim(form.postcode.value),
                state: $.trim(form.county.value)
            }
        }
    };

    // Post to the cache_checkout_data view
    $.post('/checkout/cache_checkout_data/', {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    }).then(function() {
        stripe.confirmCardPayment(clientSecret, paymentData).then(function(result) {
            if (result.error) {
                showError(result.error.message);
                resetForm();
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    // Add a hidden input with the stripe PID
                    $('<input>').attr({
                        type: 'hidden',
                        name: 'stripe_pid',
                        value: result.paymentIntent.id,
                    }).appendTo(form);
                    form.submit();
                }
            }
        });
    }).fail(function(response) {
        if (response.status === 400) {
            showError('This payment has already been processed. Please check your email for order confirmation.');
        } else {
            showError('Sorry, there was a network error. Please try again.');
        }
        resetForm();
    });
});
