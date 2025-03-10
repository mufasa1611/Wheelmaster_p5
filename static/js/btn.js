$('#new-image').change(function () {
    var file = $('#new-image')[0].files[0];
    $('#filename').text(`Image will be set to: ${file.name}`);
});

$(document).ready(function () {
    // Initially hide the button
    $('.btn-btt').hide();

    // Show/hide the button based on scroll position
    $(window).scroll(function () {
        var scrollPosition = $(this).scrollTop();
        var footerOffset = $('footer').offset().top; // Get the footer position
        var windowHeight = $(window).height(); // Get the height of the viewport


        // Show button when the bottom of the viewport is within 50 pixels of the footer
        if (scrollPosition + windowHeight >= footerOffset - 50) {
            $('.btn-btt').fadeIn();

        }
        // Hide button when at the top of the page or above the footer
        else if (scrollPosition < 20) {
            $('.btn-btt').fadeOut();

        }
    });
});

$('.btn-btt').click(function (e) {
    e.preventDefault();

    $('html, body').animate({
        scrollTop: 0
    }, 1500, function () {

    });
});