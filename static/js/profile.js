// static/js/profile.js - UPDATED VERSION

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initImageUpload();
    initVideoOptions();
    
    // Initialize cropper if not already loaded
    if (typeof ImageCropper === 'undefined') {
        loadCropperScript();
    }
});

function initImageUpload() {
    // Profile picture upload
    const avatarCircle = document.getElementById('avatar-circle');
    const pfpUpload = document.getElementById('pfp-upload');
    
    if (avatarCircle && pfpUpload) {
        avatarCircle.addEventListener('click', function() {
            pfpUpload.click();
        });
        
        pfpUpload.addEventListener('change', function(event) {
            const aspectRatio = avatarCircle.getAttribute('data-aspect-ratio');
            const type = avatarCircle.getAttribute('data-upload-type');
            handleImageUpload(event, type, aspectRatio);
        });
    }
    
    // Banner upload
    const profileBanner = document.getElementById('profile-banner');
    const bannerUpload = document.getElementById('banner-upload');
    
    if (profileBanner && bannerUpload) {
        profileBanner.addEventListener('click', function() {
            bannerUpload.click();
        });
        
        bannerUpload.addEventListener('change', function(event) {
            const aspectRatio = profileBanner.getAttribute('data-aspect-ratio');
            const type = profileBanner.getAttribute('data-upload-type');
            handleImageUpload(event, type, aspectRatio);
        });
    }
}

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

function handleImageUpload(event, type, aspectRatio) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    if (!file.type.match('image.*')) {
        showNotification('Please select an image file (JPEG, PNG, etc.)', 'error');
        return;
    }
    
    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showNotification('Image size should be less than 10MB', 'error');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        // Ensure cropper is loaded
        if (typeof ImageCropper === 'undefined') {
            showNotification('Loading image editor...', 'info');
            setTimeout(() => {
                launchCropper(e.target.result, type, aspectRatio);
            }, 500);
        } else {
            launchCropper(e.target.result, type, aspectRatio);
        }
    };
    
    reader.onerror = function() {
        showNotification('Error reading image file', 'error');
    };
    
    reader.readAsDataURL(file);
    
    // Reset input value to allow uploading same file again
    event.target.value = '';
}

function launchCropper(imageSrc, type, aspectRatio) {
    const cropper = new ImageCropper({
        container: document.body,
        imageSrc: imageSrc,
        aspectRatio: aspectRatio,
        cropType: type, // 'pfp' or 'banner'
        onCrop: function(croppedImageUrl, blob) {
            uploadCroppedImage(blob, type);
        },
        onCancel: function() {
            console.log('Cropping cancelled');
        }
    });
}

function uploadCroppedImage(blob, type) {
    showNotification('Uploading image...', 'info');
    
    const formData = new FormData();
    const csrfToken = getCsrfToken();
    
    // Generate filename
    const timestamp = new Date().getTime();
    const filename = `${type}_${timestamp}.jpg`;
    
    formData.append('image', blob, filename);
    formData.append('type', type);
    
    // Determine upload URL based on user role
    const uploadUrl = '/api/upload-profile-image/';
    
    fetch(uploadUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            showNotification('Image updated successfully!', 'success');
            
            // Reload page after 1 second to show updated image
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            throw new Error(data.message || 'Upload failed');
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        showNotification('Error uploading image: ' + error.message, 'error');
    });
}

function getCsrfToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    return cookieValue || '';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="bi ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles if not already present
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 80px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 9999;
                min-width: 300px;
                max-width: 400px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                transform: translateX(120%);
                transition: transform 0.3s ease;
            }
            
            .notification.show {
                transform: translateX(0);
            }
            
            .notification-info {
                background: #3498db;
                border-left: 4px solid #2980b9;
            }
            
            .notification-success {
                background: #2ecc71;
                border-left: 4px solid #27ae60;
            }
            
            .notification-error {
                background: #e74c3c;
                border-left: 4px solid #c0392b;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .notification-content i {
                font-size: 1.2rem;
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 4000);
    
    return notification;
}

function getNotificationIcon(type) {
    switch(type) {
        case 'success': return 'bi-check-circle-fill';
        case 'error': return 'bi-exclamation-circle-fill';
        case 'info': return 'bi-info-circle-fill';
        default: return 'bi-info-circle';
    }
}

function loadCropperScript() {
    // Check if script is already loaded
    if (document.querySelector('script[src*="cropper.js"]')) {
        return;
    }
    
    const script = document.createElement('script');
    script.src = '{% static "js/cropper.js" %}';
    script.onload = function() {
        console.log('Cropper script loaded successfully');
    };
    script.onerror = function() {
        console.error('Failed to load cropper script');
        showNotification('Failed to load image editor. Please refresh the page.', 'error');
    };
    document.head.appendChild(script);
}

function toggleFollow(username) {
    const followBtn = document.getElementById('follow-btn');
    const nosCount = document.getElementById('follower-count'); // Ensure your count span has this ID

    fetch(`/teacher/toggle-follow/${username}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}', // Standard Django CSRF protection
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            if (data.action === 'followed') {
                // UI update for "Following" state
                followBtn.innerHTML = '<i class="bi bi-check2"></i> Following';
                followBtn.classList.add('following-active');
                window.location.reload();
            } else {
                // UI update for "Follow" state
                followBtn.innerHTML = '<i class="bi bi-plus-lg"></i> Follow';
                followBtn.classList.remove('following-active');
                window.location.reload();
            }
            // Update the subscriber count number
            nosCount.innerText = data.new_count;
        }
        
    })
    .catch(error => console.error('Error:', error));
}