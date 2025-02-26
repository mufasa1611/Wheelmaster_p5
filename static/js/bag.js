 // Update quantity on change
function updateQuantity(itemId, size, quantity) {
    var url = `/bag/adjust/${itemId}/`;
    var data = {
        'quantity': quantity
    };
    if (size) {
        data.product_size = size;
    }

    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        success: function(response) {
            location.reload();
        },
        error: function(xhr) {
            if (xhr.responseJSON && xhr.responseJSON.error) {
                alert(xhr.responseJSON.error);
            } else {
                alert('Error updating quantity');
            }
            location.reload();
        }
    });
}

$(document).ready(function() {
    // Prevent non-numeric keys and zero
    $('.qty_input').keypress(function(e) {
        // Get the key code
        var keyCode = e.which ? e.which : e.keyCode;
        
        // Allow only keys 1-9 (key codes 49-57)
        if (keyCode < 49 || keyCode > 57) {
            e.preventDefault();
            return false;
        }
        return true;
    });

    // Handle quantity input changes
    $('.qty_input').change(function() {
        var itemId = $(this).data('item_id');
        var size = $(this).data('size') || '';
        var quantity = parseInt($(this).val());
        
        if (quantity >= 1) {
            updateQuantity(itemId, size, quantity);
        }
    });

    // Remove item and reload on click
    $('.remove-item').click(function(e) {
        e.preventDefault();
        var itemId = $(this).data('item_id');
        var size = $(this).data('size');
        var url = `/bag/remove/${itemId}/`;
        var data = {
            'product_size': size
        };

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            success: function(response) {
                location.reload();
            },
            error: function(xhr) {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    alert(xhr.responseJSON.error);
                } else {
                    alert('Error removing item');
                }
                location.reload();
            }
        });
    });

    // Quantity controls
    function handleEnableDisable(itemId, size) {
        var currentValue = parseInt($(`.qty_input[data-item_id='${itemId}'][data-size='${size}']`).val());
        var maxAvailable = parseInt($(`.qty_input[data-item_id='${itemId}'][data-size='${size}']`).attr('max'));
        var minusDisabled = currentValue < 2;
        var plusDisabled = currentValue >= maxAvailable;

        $(`.decrement-qty[data-item_id='${itemId}'][data-size='${size}']`).prop('disabled', minusDisabled);
        $(`.increment-qty[data-item_id='${itemId}'][data-size='${size}']`).prop('disabled', plusDisabled);
    }

    // Enable/disable +/- buttons on load
    var allQtyInputs = $('.qty_input');
    for(var i = 0; i < allQtyInputs.length; i++){
        var itemId = $(allQtyInputs[i]).data('item_id');
        var size = $(allQtyInputs[i]).data('size') || '';
        handleEnableDisable(itemId, size);
    }

    // Increment quantity
    $('.increment-qty').click(function(e) {
        e.preventDefault();
        var itemId = $(this).data('item_id');
        var size = $(this).data('size') || '';
        var closestInput = $(`.qty_input[data-item_id='${itemId}'][data-size='${size}']`);
        var currentValue = parseInt(closestInput.val());
        var maxAvailable = parseInt(closestInput.attr('max'));
        
        if (currentValue < maxAvailable) {
            currentValue += 1;
            closestInput.val(currentValue);
            handleEnableDisable(itemId, size);
            updateQuantity(itemId, size, currentValue);
        }
    });

    // Decrement quantity
    $('.decrement-qty').click(function(e) {
        e.preventDefault();
        var itemId = $(this).data('item_id');
        var size = $(this).data('size') || '';
        var closestInput = $(`.qty_input[data-item_id='${itemId}'][data-size='${size}']`);
        var currentValue = parseInt(closestInput.val());
        
        if (currentValue > 1) {
            currentValue -= 1;
            closestInput.val(currentValue);
            handleEnableDisable(itemId, size);
            updateQuantity(itemId, size, currentValue);
        }
    });
});