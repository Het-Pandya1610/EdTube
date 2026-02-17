document.addEventListener('DOMContentLoaded', function() {
    initVideoOptions();
});

function initVideoOptions() {
    // Add event listeners to all video options buttons
    document.querySelectorAll('.video-options-btn').forEach(button => {
        // Remove any inline onclick handlers to prevent CSP issues
        button.removeAttribute('onclick');
        
        button.addEventListener('click', function(event) {
            // Find the associated dropdown menu
            const videoCard = this.closest('.video-card-container');
            if (videoCard) {
                const dropdown = videoCard.querySelector('.options-dropdown');
                if (dropdown) {
                    toggleOptionsMenu(event, dropdown.id);
                }
            }
        });
    });
    
    // Prevent dropdown from closing when clicking inside dropdown items
    document.querySelectorAll('.options-dropdown').forEach(dropdown => {
        dropdown.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    });
    
    // Close dropdowns when clicking anywhere else on the page
    document.addEventListener('click', function() {
        document.querySelectorAll('.options-dropdown').forEach(dropdown => {
            dropdown.classList.remove('show');
        });
    });
    
    // Also close on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelectorAll('.options-dropdown').forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    });
}

function toggleOptionsMenu(event, menuId) {
    event.preventDefault();
    event.stopPropagation();
    
    // Close any other open menus
    document.querySelectorAll('.options-dropdown').forEach(m => {
        if(m.id !== menuId) m.classList.remove('show');
    });

    const menu = document.getElementById(menuId);
    if (menu) {
        menu.classList.toggle('show');
        
        // Position the dropdown if it goes off screen
        positionDropdown(menu);
    }
}

function positionDropdown(dropdown) {
    const rect = dropdown.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    
    // Check if dropdown goes off the right edge of the screen
    if (rect.right > viewportWidth) {
        dropdown.style.right = '10px';
        dropdown.style.left = 'auto';
    }
    
    // Check if dropdown goes off the bottom edge of the screen
    if (rect.bottom > window.innerHeight) {
        dropdown.style.top = 'auto';
        dropdown.style.bottom = '45px';
    }
}