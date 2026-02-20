// edit_video.js - Complete version

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const videoFile = document.getElementById('video_file');
    const thumbnail = document.getElementById('thumbnail');
    const form = document.getElementById('edit-video-form');
    const videoPreview = document.getElementById('video-preview');
    const startTime = document.getElementById('start-time');
    const endTime = document.getElementById('end-time');
    const previewTrim = document.getElementById('preview-trim');
    const applyTrim = document.getElementById('apply-trim');
    const titleInput = document.getElementById('title');
    const subjectInput = document.getElementById('subject');
    const languageSelect = document.getElementById('language');
    const descriptionInput = document.getElementById('description');
    
    // Video trimming variables
    let videoDuration = 0;
    let trimStart = 0;
    let trimEnd = 0;
    let originalVideoUrl = videoPreview ? videoPreview.querySelector('source')?.src : null;

    // Get video duration when loaded
    if (videoPreview) {
        videoPreview.addEventListener('loadedmetadata', function() {
            videoDuration = this.duration;
            const durationStr = formatTime(videoDuration);
            
            // Set end time if not already set
            if (endTime && (endTime.value === '--:--' || endTime.value === '{{ video.duration|default:"10:00" }}')) {
                endTime.value = durationStr;
                trimEnd = videoDuration;
            }
            
            // Set max attribute for time inputs
            if (startTime) startTime.max = durationStr;
            if (endTime) endTime.max = durationStr;
        });
    }

    // Format time helper (seconds to MM:SS)
    function formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '00:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // Parse time string (MM:SS) to seconds
    function parseTime(timeStr) {
        if (!timeStr) return 0;
        const parts = timeStr.split(':');
        if (parts.length === 2) {
            const mins = parseInt(parts[0]) || 0;
            const secs = parseInt(parts[1]) || 0;
            return (mins * 60) + secs;
        }
        return 0;
    }

    // Validate time inputs
    function validateTimes() {
        if (!startTime || !endTime) return false;
        
        const start = parseTime(startTime.value);
        const end = parseTime(endTime.value);
        
        // Check if times are valid numbers
        if (isNaN(start) || isNaN(end)) {
            showNotification('Invalid time format. Use MM:SS', 'error');
            return false;
        }
        
        // Check range
        if (start < 0) {
            showNotification('Start time cannot be negative', 'error');
            return false;
        }
        
        if (end > videoDuration) {
            showNotification(`End time cannot exceed ${formatTime(videoDuration)}`, 'error');
            return false;
        }
        
        if (start >= end) {
            showNotification('Start time must be less than end time', 'error');
            return false;
        }
        
        if (end - start < 1) {
            showNotification('Video segment must be at least 1 second long', 'error');
            return false;
        }
        
        trimStart = start;
        trimEnd = end;
        return true;
    }

    // Preview trim
    if (previewTrim) {
        previewTrim.addEventListener('click', function() {
            if (!validateTimes()) return;
            
            const modal = document.getElementById('trim-preview-modal');
            const previewVideo = document.getElementById('preview-video');
            const previewStart = document.getElementById('preview-start');
            const previewEnd = document.getElementById('preview-end');
            
            if (!modal || !previewVideo) return;
            
            previewStart.textContent = formatTime(trimStart);
            previewEnd.textContent = formatTime(trimEnd);
            
            // Set video to start time
            previewVideo.currentTime = trimStart;
            
            // Show modal
            modal.classList.add('show');
            
            // Play preview
            previewVideo.play().catch(e => console.log('Autoplay prevented:', e));
            
            // Stop at end time
            previewVideo.ontimeupdate = function() {
                if (this.currentTime >= trimEnd) {
                    this.pause();
                    this.currentTime = trimStart;
                }
            };
        });
    }

    // Apply trim
    if (applyTrim) {
        applyTrim.addEventListener('click', async function() {
            if (!validateTimes()) return;
            
            // Confirm with user
            if (!confirm('Are you sure you want to trim the video? This will create a new version.')) {
                return;
            }
            
            // Show loader
            if (typeof pageLoader !== 'undefined') {
                pageLoader.show({
                    message: 'Trimming video...',
                    submessage: 'This may take a few moments',
                    type: 'upload',
                    showProgress: true
                });
            }
            
            try {
                // Get video ID from URL or data attribute
                const videoId = window.location.pathname.split('/').filter(Boolean).pop();
                
                // Create form data for trimming
                const formData = new FormData();
                formData.append('video_id', videoId);
                formData.append('start_time', trimStart);
                formData.append('end_time', trimEnd);
                formData.append('action', 'trim');
                
                const response = await fetch('/api/trim-video/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCsrfToken()
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Update progress
                    if (typeof pageLoader !== 'undefined') {
                        pageLoader.updateProgress(100, 'Trim complete!');
                    }
                    
                    // Show success message
                    showNotification('Video trimmed successfully', 'success');
                    
                    // Update video source with cache busting
                    if (videoPreview) {
                        const source = videoPreview.querySelector('source');
                        if (source) {
                            const newUrl = data.new_url || source.src;
                            source.src = newUrl + '?t=' + Date.now();
                            videoPreview.load();
                        }
                    }
                    
                    // Update duration display
                    if (endTime) {
                        endTime.value = formatTime(trimEnd - trimStart);
                    }
                    
                    setTimeout(() => {
                        if (typeof pageLoader !== 'undefined') {
                            pageLoader.hide();
                        }
                    }, 1000);
                } else {
                    throw new Error(data.message || 'Trim failed');
                }
            } catch (error) {
                console.error('Trim error:', error);
                if (typeof pageLoader !== 'undefined') {
                    pageLoader.hide();
                }
                showNotification('Trim failed: ' + error.message, 'error');
            }
        });
    }

    // Preview thumbnail on file select
    if (thumbnail) {
        thumbnail.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                if (!file.type.match('image.*')) {
                    showNotification('Please select an image file', 'error');
                    thumbnail.value = '';
                    return;
                }
                
                // Validate file size (max 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    showNotification('Image size should be less than 5MB', 'error');
                    thumbnail.value = '';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    const currentThumb = document.getElementById('current-thumbnail');
                    if (currentThumb) {
                        currentThumb.src = e.target.result;
                    } else {
                        // Create new thumbnail preview
                        const thumbDiv = document.querySelector('.current-thumbnail');
                        if (thumbDiv) {
                            thumbDiv.innerHTML = `<img src="${e.target.result}" alt="New thumbnail" id="current-thumbnail">`;
                        }
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Preview video file on select
    if (videoFile) {
        videoFile.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                if (!file.type.match('video.*')) {
                    showNotification('Please select a video file', 'error');
                    videoFile.value = '';
                    return;
                }
                
                // Validate file size (max 500MB)
                if (file.size > 500 * 1024 * 1024) {
                    showNotification('Video size should be less than 500MB', 'error');
                    videoFile.value = '';
                    return;
                }
                
                // Show warning about replace
                if (!confirm('Uploading a new video will replace the current one. Continue?')) {
                    videoFile.value = '';
                    return;
                }
                
                // Create video preview
                const url = URL.createObjectURL(file);
                if (videoPreview) {
                    const source = videoPreview.querySelector('source');
                    if (source) {
                        source.src = url;
                        videoPreview.load();
                    }
                }
                
                // Update duration when loaded
                videoPreview.onloadedmetadata = function() {
                    videoDuration = this.duration;
                    const durationStr = formatTime(videoDuration);
                    if (endTime) {
                        endTime.value = durationStr;
                        trimEnd = videoDuration;
                    }
                    showNotification('New video loaded. Click Save to apply changes.', 'info');
                };
            }
        });
    }

    // Form validation before submit
    function validateForm() {
        if (!titleInput || !titleInput.value.trim()) {
            showNotification('Title is required', 'error');
            titleInput?.focus();
            return false;
        }
        
        if (!subjectInput || !subjectInput.value.trim()) {
            showNotification('Subject is required', 'error');
            subjectInput?.focus();
            return false;
        }
        
        if (!languageSelect || !languageSelect.value) {
            showNotification('Please select a language', 'error');
            languageSelect?.focus();
            return false;
        }
        
        return true;
    }

    // Form submission
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Validate form
            if (!validateForm()) {
                return;
            }
            
            // Show loader
            if (typeof pageLoader !== 'undefined') {
                pageLoader.show({
                    message: 'Saving changes...',
                    submessage: 'Please wait while we update your video',
                    type: 'upload',
                    showProgress: true
                });
            }

            try {
                // MANUALLY create FormData and add ALL fields
                const formData = new FormData();
                
                // Get CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                formData.append('csrfmiddlewaretoken', csrfToken);
                
                // MANUALLY add all form fields with values
                formData.append('title', document.getElementById('title').value);
                formData.append('description', document.getElementById('description').value);
                formData.append('subject', document.getElementById('subject').value);
                formData.append('language', document.getElementById('language').value);
                formData.append('action', 'update');
                
                // Add thumbnail if selected
                const thumbnailFile = document.getElementById('thumbnail').files[0];
                if (thumbnailFile) {
                    formData.append('thumbnail', thumbnailFile);
                }
                
                // Add video file if selected
                const videoFile = document.getElementById('video_file').files[0];
                if (videoFile) {
                    formData.append('video_file', videoFile);
                }
                
                // Add video type info
                const hasVideoFile = document.querySelector('.info-badge span')?.textContent === 'Uploaded Video File';
                formData.append('has_video_file', hasVideoFile ? 'true' : 'false');
                
                // DEBUG: Log what we're sending
                console.log('=== SENDING FORM DATA ===');
                for (let pair of formData.entries()) {
                    if (pair[0] !== 'csrfmiddlewaretoken') {
                        console.log(pair[0] + ':', pair[1] instanceof File ? pair[1].name : pair[1]);
                    }
                }
                
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                });

                if (response.redirected) {
                    if (typeof pageLoader !== 'undefined') {
                        pageLoader.updateProgress(100, 'Changes saved! Redirecting...');
                    }
                    showNotification('Video updated successfully', 'success');
                    window.location.href = response.url;
                    return;
                }

                // Check if response is JSON
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    if (data.status === 'success') {
                        showNotification('Video updated successfully', 'success');
                        setTimeout(() => {
                            window.location.href = data.redirect_url || '/profile/';
                        }, 1500);
                    } else {
                        throw new Error(data.message || 'Failed to save');
                    }
                } else {
                    // If HTML response, something went wrong
                    const text = await response.text();
                    console.error('Unexpected HTML response:', text.substring(0, 200));
                    throw new Error('Server error - check console');
                }
                
            } catch (error) {
                console.error('Save error:', error);
                if (typeof pageLoader !== 'undefined') {
                    pageLoader.hide();
                }
                showNotification(error.message || 'Failed to save changes', 'error');
            }
        });
    }

    // Modal close functionality
    const modal = document.getElementById('trim-preview-modal');
    if (modal) {
        // Close with close button
        document.querySelectorAll('.close-modal, .close-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                modal.classList.remove('show');
                const previewVideo = document.getElementById('preview-video');
                if (previewVideo) {
                    previewVideo.pause();
                }
            });
        });

        // Apply trim from preview
        const applyFromPreview = document.querySelector('.apply-trim-from-preview');
        if (applyFromPreview) {
            applyFromPreview.addEventListener('click', function() {
                modal.classList.remove('show');
                if (applyTrim) {
                    applyTrim.click();
                }
            });
        }

        // Close on click outside
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('show');
                const previewVideo = document.getElementById('preview-video');
                if (previewVideo) {
                    previewVideo.pause();
                }
            }
        });
    }

    // Auto-format time inputs
    if (startTime) {
        startTime.addEventListener('blur', function() {
            const seconds = parseTime(this.value);
            this.value = formatTime(seconds);
        });
    }
    
    if (endTime) {
        endTime.addEventListener('blur', function() {
            const seconds = parseTime(this.value);
            this.value = formatTime(seconds);
        });
    }

    // Character count for title
    if (titleInput) {
        const titleCounter = document.createElement('small');
        titleCounter.className = 'char-counter';
        titleInput.parentNode.appendChild(titleCounter);
        
        const updateTitleCounter = () => {
            const count = titleInput.value.length;
            titleCounter.textContent = `${count}/200 characters`;
            titleCounter.style.color = count > 180 ? '#dc3545' : '#666';
        };
        
        titleInput.addEventListener('input', updateTitleCounter);
        updateTitleCounter();
    }

    // Warn before leaving if form is dirty
    let formDirty = false;
    
    const markDirty = () => { formDirty = true; };
    
    [titleInput, subjectInput, descriptionInput, languageSelect].forEach(field => {
        if (field) field.addEventListener('change', markDirty);
        if (field && field.type !== 'select-one') {
            field.addEventListener('input', markDirty);
        }
    });
    
    if (thumbnail) thumbnail.addEventListener('change', markDirty);
    if (videoFile) videoFile.addEventListener('change', markDirty);

    window.addEventListener('beforeunload', function(e) {
        if (formDirty && !form.hasAttribute('data-submitting')) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    });
});

// CSRF Token helper - IMPROVED VERSION
function getCsrfToken() {
    // Try to get from cookie first
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    if (cookieValue) {
        console.log('CSRF from cookie:', cookieValue);
        return cookieValue;
    }
    
    // Fallback: get from hidden input
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        console.log('CSRF from input:', csrfInput.value);
        return csrfInput.value;
    }
    
    console.error('CSRF token not found!');
    return '';
}

// Notification helper
function showNotification(message, type = 'info') {
    // Use existing showNotification if available
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
        return;
    }
    
    // Create notification if function doesn't exist
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#17a2b8'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10001;
        animation: slideIn 0.3s ease;
        font-weight: 500;
    `;
    
    // Add icon based on type
    const icon = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';
    notification.innerHTML = `${icon} ${message}`;
    
    document.body.appendChild(notification);
    
    // Add animation keyframes if not exists
    if (!document.querySelector('#notification-keyframes')) {
        const style = document.createElement('style');
        style.id = 'notification-keyframes';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}