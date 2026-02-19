// static/js/profile.js - UPDATED VERSION WITH OPTIMIZED FOLLOW TOGGLE

// Cache for CSRF token
let cachedCsrfToken = null;

// Map to track ongoing follow requests for debouncing
const followRequests = new Map();

// Loading states for buttons
const loadingStates = new Map();

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initImageUpload();
    initVideoOptions();
    initVideoActions();
    // Initialize cropper if not already loaded
    if (typeof ImageCropper === 'undefined') {
        loadCropperScript();
    }
    
    // Add spinner styles if not present
    addSpinnerStyles();
});

function addSpinnerStyles() {
    if (!document.querySelector('#spinner-style')) {
        const style = document.createElement('style');
        style.id = 'spinner-style';
        style.textContent = `
            .spinning {
                animation: spin 1s linear infinite;
                display: inline-block;
            }
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
            .btn-loading {
                opacity: 0.8;
                cursor: wait;
                pointer-events: none;
            }
            
            .btn-loading i {
                animation: spin 1s linear infinite;
            }
        `;
        document.head.appendChild(style);
    }
}

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
function initVideoActions(){
    document.querySelectorAll('.dropdown-item:has(.bi-pencil)').forEach(editBtn => {
        editBtn.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            
            // Find the video card container
            const videoCard = this.closest('.video-card-container');
            if (videoCard) {
                const videoId = videoCard.querySelector('.video-options-btn')?.getAttribute('data-video-id');
                if (videoId) {
                    openVideoEditor(videoId);
                }
            }
        });
    });
    document.querySelectorAll('.dropdown-item.delete-opt, .dropdown-item:has(.bi-trash)').forEach(deleteBtn => {
        deleteBtn.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            
            // Find the video card container
            const videoCard = this.closest('.video-card-container');
            if (videoCard) {
                const videoId = videoCard.querySelector('.video-options-btn')?.getAttribute('data-video-id');
                const videoTitle = videoCard.querySelector('.v-title')?.textContent || 'this video';
                if (videoId) {
                    confirmDeleteVideo(videoId, videoTitle);
                }
            }
        });
    });
}

// Open video editor modal/page
function openVideoEditor(videoId) {
    // Option 1: Redirect to edit page
    window.location.href = `/video/edit/${videoId}/`;
    
    // Option 2: Open modal (if you prefer inline editing)
    // loadEditModal(videoId);
}

// Confirm delete with modal
function confirmDeleteVideo(videoId, videoTitle) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'delete-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="bi bi-exclamation-triangle"></i> Delete Video</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <p>Are you sure you want to delete <strong>"${videoTitle}"</strong>?</p>
                <p class="warning-text">This action cannot be undone. All video data, comments, and analytics will be permanently removed.</p>
            </div>
            <div class="modal-footer">
                <button class="cancel-btn">Cancel</button>
                <button class="delete-btn" id="confirm-delete-btn">Delete Permanently</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add modal styles
    addModalStyles();
    
    // Show modal with animation
    setTimeout(() => modal.classList.add('show'), 10);
    
    // Handle close
    modal.querySelector('.modal-close').addEventListener('click', () => {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    });
    
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    });
    
    // Handle delete confirmation
    modal.querySelector('#confirm-delete-btn').addEventListener('click', async () => {
        // Show loading state
        const deleteBtn = modal.querySelector('#confirm-delete-btn');
        deleteBtn.innerHTML = '<i class="bi bi-arrow-repeat spinning"></i> Deleting...';
        deleteBtn.disabled = true;
        
        try {
            await deleteVideo(videoId);
            
            // Show success message
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
            
            // Remove video card from UI
            const videoCard = document.querySelector(`[data-video-id="${videoId}"]`)?.closest('.video-card-container');
            if (videoCard) {
                videoCard.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => videoCard.remove(), 300);
            }
            
            // Update video count if exists
            updateVideoCount();
            
            showNotification('Video deleted successfully', 'success');
            window.location.reload();
        } catch (error) {
            console.error('Delete error:', error);
            showNotification('Failed to delete video: ' + error.message, 'error');
            
            // Reset button
            deleteBtn.innerHTML = 'Delete Permanently';
            deleteBtn.disabled = false;
        }
    });
    
    // Close on click outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
        }
    });
}

// Delete video API call
async function deleteVideo(videoId) {
    const csrfToken = getCsrfToken();
    
    const response = await fetch(`/video/delete/${videoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Delete failed');
    }
    
    return await response.json();
}

// Update video count after deletion
function updateVideoCount() {
    const videoCountElement = document.querySelector('.stat-item:has(.stat-count) .stat-count');
    if (videoCountElement) {
        const currentCount = parseInt(videoCountElement.textContent) || 0;
        videoCountElement.textContent = currentCount - 1;
    }
}

// Add modal styles
function addModalStyles() {
    if (document.getElementById('modal-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'modal-styles';
    style.textContent = `
        .delete-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(5px);
            z-index: 10000;
            display: flex;
            justify-content: center;
            align-items: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .delete-modal.show {
            opacity: 1;
        }
        
        .modal-content {
            background: var(--bg-color) !important;
            border-radius: 16px;
            width: 90%;
            padding: 40px 40px;
            max-width: 500px;
            transform: scale(0.9);
            transition: transform 0.3s ease;
            box-shadow: 0 20px 60px var(--srch-bg-color);
            border: 1px solid var(--srch-bg-color);
        }
        
        .delete-modal.show .modal-content {
            transform: scale(1);
        }
        
        .modal-header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--text-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-header h3 {
            margin: 0;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 10px;
            color: #dc3545;
        }
        
        .modal-header i {
            font-size: 1.5rem;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: 1.8rem;
            cursor: pointer;
            color: var(--text-color);
            opacity: 0.6;
            transition: opacity 0.3s;
        }
        
        .modal-close:hover {
            opacity: 1;
        }
        
        .modal-body {
            padding: 24px;
        }
        
        .modal-body p {
            margin: 10px 0;
            font-size: 1.1rem;
            color: var(--text-color);
        }
        
        .warning-text {
            color: #dc3545 !important;
            font-size: 0.95rem !important;
            background: rgba(220, 53, 69, 0.1);
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #dc3545;
        }
        
        .modal-footer {
            padding: 20px 24px;
            border-top: 1px solid var(--text-color);
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }
        
        .modal-footer button {
            padding: 10px 24px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
        }
        
        .cancel-btn {
            background: none;
            border: 2 px solid (--text-color) !important;
            color: var(--text-color);
            transition: 0.3s all;
        }
        
        .cancel-btn:hover {
            background: var(--text-color);
            color: var(--bg-color);
        }
        
        .delete-btn {
            background: #dc3545;
            color: white;
        }
        
        .delete-btn:hover {
            background: #c82333;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(220, 53, 69, 0.3);
        }
        
        .delete-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        @keyframes slideOut {
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .spinning {
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 5px;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    `;
    
    document.head.appendChild(style);
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

// Optimized CSRF token getter with caching
function getCsrfToken() {
    if (cachedCsrfToken) return cachedCsrfToken;
    
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    cachedCsrfToken = cookieValue || '';
    return cachedCsrfToken;
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

// OPTIMIZED FOLLOW TOGGLE HANDLER - FIXED VERSION
document.addEventListener('click', function (event) {
    const followBtn = event.target.closest('#follow-btn');
    
    if (followBtn) {
        event.preventDefault();
        
        // Prevent multiple rapid clicks
        if (followBtn.disabled || followBtn.classList.contains('btn-loading')) {
            return;
        }

        const username = followBtn.getAttribute('data-teacher-username');
        
        // Debounce check
        if (followRequests.has(username)) {
            const lastRequest = followRequests.get(username);
            if (Date.now() - lastRequest < 2000) { // Increased to 2 seconds
                showNotification('Please wait...', 'info');
                return;
            }
        }
        followRequests.set(username, Date.now());

        const nosCount = document.getElementById('follower-count');
        const currentCount = parseInt(nosCount?.innerText || '0');
        const isCurrentlyFollowing = followBtn.classList.contains('following-active');
        
        // Store original state for rollback
        const originalState = {
            html: followBtn.innerHTML,
            isFollowing: isCurrentlyFollowing,
            count: currentCount
        };
        
        // DISABLE BUTTON COMPLETELY
        followBtn.disabled = true;
        followBtn.classList.add('btn-loading');
        
        // Show loading state
        followBtn.innerHTML = '<i class="bi bi-arrow-repeat spinning"></i>';
        
        // DON'T update the count optimistically - wait for server
        // Only update the button text to show intent
        if (isCurrentlyFollowing) {
            followBtn.innerHTML = '<i class="bi bi-arrow-repeat spinning"></i> Unfollowing...';
        } else {
            followBtn.innerHTML = '<i class="bi bi-arrow-repeat spinning"></i> Following...';
        }

        const csrftoken = getCsrfToken();

        fetch(`/teacher/toggle-follow/${username}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // Update with server's count (always accurate)
                if (nosCount && data.new_count !== undefined) {
                    nosCount.innerText = data.new_count;
                }
                
                // Update button based on server response
                if (data.action === 'followed') {
                    followBtn.innerHTML = '<i class="bi bi-check2"></i> Following';
                    followBtn.classList.add('following-active');
                } else {
                    followBtn.innerHTML = '<i class="bi bi-plus-lg"></i> Follow';
                    followBtn.classList.remove('following-active');
                }
                
                showNotification(
                    data.action === 'followed' ? `Followed @${username}` : `Unfollowed @${username}`, 
                    'success'
                );
            } else {
                throw new Error(data.message || 'Failed to update follow status');
            }
        })
        .catch(error => {
            console.error('Follow error:', error);
            
            // Rollback to original state on error
            followBtn.innerHTML = originalState.html;
            if (originalState.isFollowing) {
                followBtn.classList.add('following-active');
            } else {
                followBtn.classList.remove('following-active');
            }
            if (nosCount) {
                nosCount.innerText = originalState.count;
            }
            
            showNotification('Error updating follow status', 'error');
        })
        .finally(() => {
            // Re-enable button
            followBtn.disabled = false;
            followBtn.classList.remove('btn-loading');
            
            // Clean up debounce
            setTimeout(() => {
                followRequests.delete(username);
            }, 2000);
        });
    }
});

document.addEventListener('touchstart', function (event) {
    const followBtn = event.target.closest('#follow-btn');
    if (followBtn) {
        // Prevent double-tap zoom on follow button
        event.preventDefault();
    }
}, { passive: false });

// Optional: Add keyboard shortcut for accessibility (Enter key)
document.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        const followBtn = document.activeElement.closest('#follow-btn');
        if (followBtn) {
            event.preventDefault();
            followBtn.click();
        }
    }
});