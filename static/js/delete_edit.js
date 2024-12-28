$(document).ready(function () {
    let productId;

    // Open modal on delete button click
    $('.delete-button').on('click', function () {
        productId = $(this).data('product-id');
        $('#deleteMessage').text('Are you sure you want to delete this product?'); 
        $('#confirmDelete').show(); 
        $('#cancelDelete').text('Cancel'); 
        $('#deleteModal').fadeIn(); 
    });

    // Confirm deletion
    $('#confirmDelete').on('click', function () {
        $.ajax({
            type: 'DELETE',
            url: '/products/delete/' + productId + '/',
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function () {
                // Remove product from DOM
                $(`.delete-button[data-product-id="${productId}"]`).closest('.col-sm-6').fadeOut(function () {
                    $(this).remove();
                });

                // Update message and hide confirm button
                $('#deleteMessage').text('Product deleted successfully!');
                $('#confirmDelete').hide();
                $('#cancelDelete').text('Close');
            },
            error: function (xhr) {
                // Display error message
                $('#deleteMessage').text('Error deleting product: ' + xhr.responseText);
                $('#confirmDelete').hide(); 
                $('#cancelDelete').text('Close'); 
            }
        });
    });

    // Cancel deletion and close modal
    $('#cancelDelete').on('click', function () {
        $('#deleteModal').fadeOut();
    });

    // Edit button click
    $('.edit-button').on('click', function() {
        var url = $(this).data('url');
        window.location.href = url;
      });
    });
