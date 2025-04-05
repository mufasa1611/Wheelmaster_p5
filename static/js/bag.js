// Utility Functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            }
        });
    }
    return cookieValue;
}

// AJAX Setup
$.ajaxSetup({
    headers: { 'X-CSRFToken': getCookie('csrftoken') }
});

// Loading Indicator Functions
function showLoadingIndicator(message = "Processing...") {
    $('#loading-indicator').text(message).show();
}

function hideLoadingIndicator() {
    $('#loading-indicator').hide();
}

// Disable Buttons During Requests
function disableButtons() {
    $('.decrement-qty, .increment-qty').prop('disabled', true);
}

function enableButtons() {
    $('.decrement-qty, .increment-qty').prop('disabled', false);
}

// Prevent Duplicate Requests
let requestQueue = [];
let isProcessingRequest = false;

function processNextRequest() {
    if (requestQueue.length > 0 && !isProcessingRequest) {
        isProcessingRequest = true;
        const { url, data, successCallback, errorCallback } = requestQueue.shift();

        $.ajax({
            url: url,
            method: 'POST',
            data: data,
            success: function(response) {
                isProcessingRequest = false;
                successCallback(response);
                processNextRequest(); // Process the next request in queue
            },
            error: function(xhr) {
                isProcessingRequest = false;
                errorCallback(xhr);
                processNextRequest(); // Continue with the next request
            }
        });
    }
}

function queueRequest(url, data, successCallback, errorCallback) {
    requestQueue.push({ url, data, successCallback, errorCallback });
    processNextRequest();
}

// Update Quantity Function
function updateQuantity(itemId, size, quantity) {
    const url = `/bag/adjust/${itemId}/`;
    const csrfToken = getCookie('csrftoken');
    const data = {
        'csrfmiddlewaretoken': csrfToken,
        'quantity': quantity
    };
    if (size) {
        data.product_size = size;
    }

    showLoadingIndicator();
    disableButtons();

    queueRequest(
        url,
        data,
        function(response) {
            location.reload();
        },
        function(xhr) {
            showToast(xhr.responseJSON?.error || 'Error updating quantity');
            location.reload();
        }
    );
}

// Handle Enabling/Disabling Buttons
function handleEnableDisable(itemId, size) {
    const qtyInputs = $(`.qty_input[data-item_id='${itemId}']`);
    const qtyInput = $(`.qty_input[data-item_id='${itemId}'][data-size='${size}']`);
    const currentValue = parseInt(qtyInput.val()) || 0; // Current value for specific size
    const maxStock = parseInt(qtyInput.attr('max')) || 0; // Max stock for the item

    // Calculate total quantity across all sizes
    const totalQuantity = Array.from(qtyInputs).reduce((sum, input) => {
        return sum + (parseInt($(input).val()) || 0);
    }, 0);

    // Update button states
    const minusDisabled = currentValue < 2;
    const plusDisabled = totalQuantity >= maxStock;

    // Apply states to the buttons for the current size
    $(`.decrement-qty[data-item_id='${itemId}'][data-size='${size}']`).prop('disabled', minusDisabled);
    $(`.increment-qty[data-item_id='${itemId}'][data-size='${size}']`).prop('disabled', plusDisabled);
}

// Document Ready
$(document).ready(function() {
    // Initialize Button States
    $('.qty_input').each(function() {
        const itemId = $(this).data('item_id');
        const size = $(this).data('size') || '';
        handleEnableDisable(itemId, size);
    });

    // Input Change Handler
    $('.qty_input').change(function() {
        const itemId = $(this).data('item_id');
        const size = $(this).data('size') || '';
        const quantity = parseInt($(this).val()) || 0;

        if (quantity >= 1) {
            updateQuantity(itemId, size, quantity);
        }
    });

    // Increment Quantity
    $('.increment-qty').click(function(e) {
        e.preventDefault();
        const itemId = $(this).data('item_id');
        const size = $(this).data('size') || '';
        const qtyInput = $(`.qty_input[data-item_id='${itemId}'][data-size='${size}']`);
        let currentValue = parseInt(qtyInput.val()) || 0; // Ensure numeric value
        const maxStock = parseInt(qtyInput.attr('max')) || 0; // Ensure numeric value

        if (currentValue < maxStock) {
            currentValue += 1;
            qtyInput.val(currentValue);
            handleEnableDisable(itemId, size);
            updateQuantity(itemId, size, currentValue);
        } else {
            showToast('Maximum stock reached.', 'error');
            handleEnableDisable(itemId, size); // Refresh button states
        }
    });

    // Decrement Quantity
    $('.decrement-qty').click(function(e) {
        e.preventDefault();
        const itemId = $(this).data('item_id');
        const size = $(this).data('size') || '';
        const qtyInput = $(`.qty_input[data-item_id='${itemId}'][data-size='${size}']`);
        let currentValue = parseInt(qtyInput.val()) || 0; // Ensure numeric value

        if (currentValue > 1) {
            currentValue -= 1;
            qtyInput.val(currentValue);
            handleEnableDisable(itemId, size);
            updateQuantity(itemId, size, currentValue);
        }
    });

    // Remove Item
    $('.remove-item').click(function(e) {
        e.preventDefault();
        const itemId = $(this).data('item_id');
        const size = $(this).data('size');
        const csrfToken = getCookie('csrftoken');
        const data = {
            'csrfmiddlewaretoken': csrfToken,
            'product_size': size
        };

        queueRequest(
            `/bag/remove/${itemId}/`,
            data,
            function(response) {
                location.reload();
            },
            function(xhr) {
                showToast(xhr.responseJSON?.error || 'Error removing item');
            }
        );
    });
});