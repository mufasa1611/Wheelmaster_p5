$('#new-image').change(function() {
    var file = $('#new-image')[0].files[0];
    $('#filename').text(`Image will be set to: ${file.name}`);
});

$('.btn-btt').click(function(e) {
    e.preventDefault();
    $('html, body').animate({
        scrollTop: 0
    }, 1500);
});