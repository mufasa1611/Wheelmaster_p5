document.addEventListener('DOMContentLoaded', function() {
    const sortSelector = document.getElementById('sort-selector');
    if (!sortSelector) return;  // Guard clause in case element doesn't exist
    
    sortSelector.addEventListener('change', function(event) {  // Changed to regular function
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
});