
    let countrySelected = $('#id_default_country').val();
    if (!countrySelected) {
        $('#id_default_country').css('color', '#8aafd4');
    }
    $('#id_default_country').change(function() {
        countrySelected = $(this).val();
        if (!countrySelected) {
            $(this).css('color', '#aab7c4');
        } else {
            $(this).css('color', '#000');
        }
    });


$('#profile-update-form').on('submit', function(e) 
{
    let countrySelected = $('#id_default_country').val();
    if (!countrySelected) {
        e.preventDefault(); 
        alert('Please select a country if you Belong one.');
    }
});
