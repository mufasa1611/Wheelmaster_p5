// Disable +/- buttons outside 1-99 range
function handleEnableDisable(itemId) {
    var currentValue = parseInt($(`#id_qty_${itemId}`).val());
    var minusDisabled = currentValue < 2; // Disable if less than 2
    var plusDisabled = currentValue > 98; // Disable if more than 98
    $(`#decrement-qty_${itemId}`).prop('disabled', minusDisabled);
    $(`#increment-qty_${itemId}`).prop('disabled', plusDisabled);
}

// Ensure proper enabling/disabling of all inputs on page load
$('.qty_input').each(function () {
    var itemId = $(this).data('item_id');
    handleEnableDisable(itemId);
});

// Check enable/disable every time the input is changed
$('.qty_input').change(function () {
    var itemId = $(this).data('item_id');
    handleEnableDisable(itemId);
});

// Increment quantity
$('.increment-qty').click(function (e) {
    e.preventDefault();
    var closestInput = $(this).closest('.input-group').find('.qty_input')[0];
    var currentValue = parseInt($(closestInput).val());
    $(closestInput).val(currentValue + 1);
    var itemId = $(this).data('item_id');
    handleEnableDisable(itemId);
});

// Decrement quantity
$('.decrement-qty').click(function (e) {
    e.preventDefault();
    var closestInput = $(this).closest('.input-group').find('.qty_input')[0];
    var currentValue = parseInt($(closestInput).val());
    
    // Prevent going below 1
    if (currentValue > 1) {
        $(closestInput).val(currentValue - 1);
        var itemId = $(this).data('item_id');
        handleEnableDisable(itemId);
    }
});