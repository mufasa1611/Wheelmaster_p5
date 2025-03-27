document.addEventListener('DOMContentLoaded', function() {
    // Dropdown sorting functionality
    const sortSelector = document.getElementById('sort-selector');
    if (sortSelector) {
        sortSelector.addEventListener('change', function(event) {
            const value = event.target.value;
            const url = new URL(window.location.href);

            if (value === 'None_None') {
                url.searchParams.delete('sort');
                url.searchParams.delete('direction');
            } else {
                const [sort, direction] = value.split('_');
                url.searchParams.set('sort', sort);
                url.searchParams.set('direction', direction);
            }
            window.location.href = url.toString();
        });

        // Set the current sort option
        const urlParams = new URLSearchParams(window.location.search);
        const currentSort = urlParams.get('sort') || 'None';
        const currentDirection = urlParams.get('direction') || 'None';
        const currentSorting = `${currentSort}_${currentDirection}`;

        for (let option of sortSelector.options) {
            if (option.value === currentSorting) {
                option.selected = true;
                break;
            }
        }
    }

    // Navigation dropdown functionality
    $('.dropdown-submenu').on("mouseenter", function(e){
        var menu = $(this).find('.dropdown-menu');
        var menuPos = $(this).offset();
        
        // Ensure submenu doesn't go off-screen
        if (menuPos.left + menu.width() * 2 > $(window).width()) {
            menu.css({
                left: 'auto',
                right: '100%'
            });
        }
    });

    // Automatically show dropdown menu on hover for desktop
    $('.dropdown-submenu').on("mouseenter", function() {
        $(this).find('.dropdown-menu').stop(true, true).slideDown(200);
    }).on("mouseleave", function() {
        $(this).find('.dropdown-menu').stop(true, true).slideUp(200);
    });

    // Add touch support for mobile
    $('.dropdown-submenu > a').on("click touchstart", function(e) {
        e.preventDefault();
        var menu = $(this).siblings('.dropdown-menu');
        
        if (menu.is(':visible')) {
            menu.stop(true, true).slideUp(200);
        } else {
            $('.dropdown-menu').slideUp(200); // Close other open menus
            menu.stop(true, true).slideDown(200);
        }
    });

    // Prevent parent links from being clicked when hovering submenu
    $('.dropdown-submenu > a').on("click", function(e){
        e.preventDefault();
        window.location = $(this).attr('href');
    });
});