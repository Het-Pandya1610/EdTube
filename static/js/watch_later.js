// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    const csrfToken = document.getElementById('csrfToken')?.value || '';
    
    // Get all remove buttons
    const removeButtons = document.querySelectorAll('.remove-btn');
    const clearAllBtn = document.getElementById('clearAllBtn');
    
    // Add click handlers to remove buttons
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const videoId = this.dataset.videoId;
            const videoCard = this.closest('.video-card');
            
            if (videoId && videoCard) {
                removeVideo(videoId, videoCard);
            }
        });
    });
    
    // Add click handler to clear all button
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function(e) {
            e.preventDefault();
            clearAllWatchLater();
        });
    }
    
    // Function to remove a video
    function removeVideo(videoId, videoCard) {
        if (!confirm('Remove this video from Watch Later?')) {
            return;
        }
        
        fetch(`/remove-from-watch-later/${videoId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the video card
                videoCard.remove();
                
                // Show success message
                showToast('Video removed from Watch Later', 'success');
                
                // Update counts
                updateCounts();
            } else {
                showToast('Error removing video', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error removing video', 'error');
        });
    }
    
    // Function to clear all videos
    function clearAllWatchLater() {
        if (!confirm('Are you sure you want to clear your entire Watch Later list?')) {
            return;
        }
        
        fetch('/clear-watch-later/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove all video cards
                document.querySelectorAll('.video-card').forEach(card => card.remove());
                
                // Show empty state
                showEmptyState();
                
                // Hide clear all button
                const clearBtn = document.getElementById('clearAllBtn');
                if (clearBtn) {
                    clearBtn.style.display = 'none';
                }
                
                // Update counts
                updateCounts();
                
                showToast('Watch Later list cleared', 'success');
            } else {
                showToast('Error clearing list', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error clearing list', 'error');
        });
    }
    
    // Function to update video counts
    function updateCounts() {
        const remainingVideos = document.querySelectorAll('.video-card').length;
        
        // Update playlist stats
        const playlistStats = document.getElementById('playlistStats');
        if (playlistStats) {
            playlistStats.textContent = `${remainingVideos} video${remainingVideos !== 1 ? 's' : ''}`;
        }
        
        // Update video count in sidebar
        const videoCount = document.getElementById('videoCount');
        if (videoCount) {
            videoCount.textContent = `${remainingVideos} video${remainingVideos !== 1 ? 's' : ''}`;
        }
        
        // Update nav badge
        const navBadge = document.getElementById('navBadge');
        if (remainingVideos > 0) {
            if (navBadge) {
                navBadge.textContent = remainingVideos;
            } else {
                const navLink = document.querySelector('.nav-link[href*="watch-later"]');
                if (navLink) {
                    const badge = document.createElement('span');
                    badge.className = 'badge';
                    badge.id = 'navBadge';
                    badge.textContent = remainingVideos;
                    navLink.appendChild(badge);
                }
            }
        } else if (navBadge) {
            navBadge.remove();
        }
        
        // Hide clear all button if no videos
        const clearBtn = document.getElementById('clearAllBtn');
        if (clearBtn && remainingVideos === 0) {
            clearBtn.style.display = 'none';
        }
    }
    
    // Function to show empty state
    function showEmptyState() {
        const videosList = document.getElementById('videosList');
        if (videosList) {
            videosList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-clock"></i>
                    </div>
                    <h3>Your Watch Later list is empty</h3>
                    <p>Save videos to watch them later!</p>
                    <a href="/" class="browse-btn">Browse Videos</a>
                </div>
            `;
        }
    }
    
    // Function to show toast notification
    function showToast(message, type = 'info') {
        // Remove existing toast
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }
        
        // Create new toast
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // Add icon based on type
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-circle';
        
        toast.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    // Optional: Update timestamps periodically
    function updateTimestamps() {
        document.querySelectorAll('.saved-time').forEach(el => {
            const timestamp = el.dataset.time;
            if (timestamp) {
                const date = new Date(timestamp);
                const now = new Date();
                const diffInSeconds = Math.floor((now - date) / 1000);
                
                let timeAgo;
                if (diffInSeconds < 60) {
                    timeAgo = `${diffInSeconds} seconds ago`;
                } else if (diffInSeconds < 3600) {
                    const minutes = Math.floor(diffInSeconds / 60);
                    timeAgo = `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
                } else if (diffInSeconds < 86400) {
                    const hours = Math.floor(diffInSeconds / 3600);
                    timeAgo = `${hours} hour${hours > 1 ? 's' : ''} ago`;
                } else {
                    const days = Math.floor(diffInSeconds / 86400);
                    timeAgo = `${days} day${days > 1 ? 's' : ''} ago`;
                }
                
                el.innerHTML = `<i class="far fa-clock"></i> ${timeAgo}`;
            }
        });
    }
    
    // Update timestamps every minute
    setInterval(updateTimestamps, 60000);
});