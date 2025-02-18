$(document).ready(function () {
    let productId;

    // Open modal on delete button click
    $('.delete-button').on('click', function () {
        productId = $(this).data('product-id');
        const productName = $(this).data('product-name');
        $('#deleteMessage').text(`Are you sure you want to delete ${productName}?`); 
        $('#confirmDelete').show(); 
        $('#cancelDelete').text('Cancel'); 
        $('#deleteModal').fadeIn(); 
    });

    // Confirm deletion
    $('#confirmDelete').on('click', function () {
        $.ajax({
            type: 'POST',
            url: '/products/delete/' + productId + '/',
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function () {
                // Check if we're on product detail page
                if (window.location.pathname.includes('/products/') && window.location.pathname.split('/').length > 3) {
                    // If on product detail page, redirect to products list
                    window.location.href = '/products/';
                } else {
                    // If on products list, refresh the page
                    location.reload();
                }
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
