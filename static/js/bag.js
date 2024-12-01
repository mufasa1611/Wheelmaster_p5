  // Update quantity on click
$('.update-link').click(function(e) {
    var form = $(this).prev('.update-form');
    form.submit();
});

// Remove item functionality
$('.remove-item').click(function(e) {
    var itemId = $(this).data('item_id');
    var size = $(this).data('product_size');
    var url = `/bag/remove/${itemId}/`;
    var data = {
        'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val(),
        'product_size': size
    };

    $.post(url, data)
        .done(function() {
            location.reload();
        })
        .fail(function() {
            location.reload();
        });
});