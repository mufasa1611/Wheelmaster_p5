// Ensure that the dropdown functionality works correctly for mobile navigation
document.addEventListener('DOMContentLoaded', function () {
    const dropdowns = document.querySelectorAll('.dropdown-toggle');

    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function (event) {
            const targetMenu = this.nextElementSibling;

            // Check if the target is a link
            if (targetMenu) {
                if (targetMenu.classList.contains('show')) {
                    targetMenu.classList.remove('show');
                } else {
                    targetMenu.classList.add('show');
                }
                event.preventDefault(); 
            }
        });
    });
});
