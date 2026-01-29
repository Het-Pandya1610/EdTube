let player;
let youtubeId = document.body.getAttribute('data-youtube-id') || '';
let playBtn = document.getElementById('playBtn');
let singleDouble = document.getElementById('singleDouble');
let videoProgressBar = document.getElementById('videoProgressBar');
let scrubberDot = document.getElementById('scrubberDot');
let hoverPreview = document.getElementById('hoverPreview');
let previewTime = document.getElementById('previewTime');
let dragPreviewLine = document.getElementById('dragPreviewLine');
let progressArea = document.getElementById('progressArea');
let timeDisplay = document.getElementById('timeDisplay');

let bufferProgress = document.getElementById('bufferProgress');
let timer;
let isDragging = false;
let isDraggingScrubber = false;
let showControlsTimeout;
let statusIcon = document.getElementById('statusIcon');
let qualityMenu = document.getElementById('qualityMenu');
let playerWrapper = document.getElementById('playerWrapper');
let videoDuration = 0;
let clickTimer;

    function onYouTubeIframeAPIReady() {
        player = new YT.Player('player', {
            videoId: youtubeId,
            playerVars: { 
                'controls': 0,
                'disablekb': 1,
                'rel': 0, 
                'modestbranding': 1, 
                'iv_load_policy': 3 
            },
            events: { 
                'onReady': onPlayerReady, 
                'onStateChange': onPlayerStateChange 
            }
        });
    }

    function onPlayerReady() {
        updateTimer();
        videoDuration = player.getDuration();
        
        // Listen for keyboard events
        window.addEventListener('keydown', handleKeyboard);
        
        // Initialize video controls
        initVideoControls();
        
        // Show controls on mouse move
        playerWrapper.addEventListener('mousemove', showVideoControls);
        playerWrapper.addEventListener('mouseleave', hideVideoControls);
        
        // Keep controls visible when interacting with them
        document.querySelector('.video-controls-overlay').addEventListener('mousemove', (e) => {
            e.stopPropagation();
            showVideoControls();
        });
    }

    function onPlayerStateChange(event) {
        if (event.data === YT.PlayerState.PLAYING) {
            playBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
            timer = setInterval(updateTimer, 100);
        } else {
            playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
            clearInterval(timer);
        }
    }

    function initVideoControls() {
        // Scrubber dot drag functionality
        scrubberDot.addEventListener('mousedown', startScrubberDrag);
        progressArea.addEventListener('mousedown', startProgressAreaDrag);
        
        // Mouse move for hover preview
        progressArea.addEventListener('mousemove', handleHoverPreview);
        progressArea.addEventListener('mouseleave', hideHoverPreview);
        
        // Global mouse events for dragging
        document.addEventListener('mousemove', handleDragMove);
        document.addEventListener('mouseup', stopDragging);
        
        // Touch events
        scrubberDot.addEventListener('touchstart', startScrubberDragTouch);
        progressArea.addEventListener('touchstart', startProgressAreaDragTouch);
        document.addEventListener('touchmove', handleTouchMove, { passive: false });
        document.addEventListener('touchend', stopDragging);
        
        // Always show scrubber dot when controls are visible
        progressArea.addEventListener('mouseenter', () => {
            if (!isDragging && !isDraggingScrubber) {
                scrubberDot.style.opacity = '1';
            }
        });
        
        progressArea.addEventListener('mouseleave', () => {
            if (!isDragging && !isDraggingScrubber) {
                scrubberDot.style.opacity = '0';
            }
        });
    }

    function startScrubberDrag(e) {
        e.preventDefault();
        e.stopPropagation();
        isDraggingScrubber = true;
        progressArea.classList.add('dragging');
        scrubberDot.style.cursor = 'grabbing';
        dragPreviewLine.style.display = 'block';
        setTimeout(() => {
            dragPreviewLine.classList.add('visible');
        }, 10);
        
        // Show hover preview during drag
        handleDragMove(e);
    }

    function startScrubberDragTouch(e) {
        if (e.touches.length === 1) {
            e.preventDefault();
            isDraggingScrubber = true;
            progressArea.classList.add('dragging');
            dragPreviewLine.style.display = 'block';
            setTimeout(() => {
                dragPreviewLine.classList.add('visible');
            }, 10);
            handleTouchMove(e);
        }
    }

    function startProgressAreaDrag(e) {
        // Only start drag if not clicking on scrubber dot
        if (e.target !== scrubberDot) {
            e.preventDefault();
            isDragging = true;
            progressArea.classList.add('dragging');
            updateProgressFromEvent(e);
        }
    }

    function startProgressAreaDragTouch(e) {
        if (e.touches.length === 1 && e.target !== scrubberDot) {
            e.preventDefault();
            isDragging = true;
            progressArea.classList.add('dragging');
            updateProgressFromTouch(e);
        }
    }

    function handleDragMove(e) {
        if (isDraggingScrubber) {
            // Drag scrubber dot
            const rect = progressArea.getBoundingClientRect();
            const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
            const percentage = x / rect.width;
            
            // Update preview line position
            dragPreviewLine.style.left = x + 'px';
            
            // Update preview time display
            if (player && player.getDuration) {
                const duration = player.getDuration();
                const previewTimeValue = duration * percentage;
                previewTime.textContent = formatTime(previewTimeValue);
                
                // Update hover preview position
                const previewX = Math.max(80, Math.min(x, rect.width - 80));
                hoverPreview.style.left = previewX + 'px';
                hoverPreview.style.display = 'block';
                setTimeout(() => {
                    hoverPreview.classList.add('visible');
                }, 10);
                
                // Show thumbnail preview
                updateThumbnailPreview(previewTimeValue);
            }
            
            // Update scrubber dot position visually
            videoProgressBar.style.width = (percentage * 100) + '%';
            
            e.preventDefault();
        } else if (isDragging) {
            // Regular progress bar drag
            updateProgressFromEvent(e);
            e.preventDefault();
        }
    }

    function handleTouchMove(e) {
        if (isDraggingScrubber && e.touches.length === 1) {
            e.preventDefault();
            const rect = progressArea.getBoundingClientRect();
            const x = Math.max(0, Math.min(e.touches[0].clientX - rect.left, rect.width));
            const percentage = x / rect.width;
            
            dragPreviewLine.style.left = x + 'px';
            
            if (player && player.getDuration) {
                const duration = player.getDuration();
                const previewTimeValue = duration * percentage;
                previewTime.textContent = formatTime(previewTimeValue);
                
                // Update scrubber position visually
                videoProgressBar.style.width = (percentage * 100) + '%';
            }
        } else if (isDragging && e.touches.length === 1) {
            e.preventDefault();
            updateProgressFromTouch(e);
        }
    }

    function stopDragging(e) {
        if (isDraggingScrubber) {
            // Hide preview with animation
            dragPreviewLine.classList.remove('visible');
            setTimeout(() => {
                dragPreviewLine.style.display = 'none';
            }, 200);
            
            hoverPreview.classList.remove('visible');
            setTimeout(() => {
                hoverPreview.style.display = 'none';
            }, 200);
            
            // Finalize scrubber drag
            const rect = progressArea.getBoundingClientRect();
            const x = e.clientX ? Math.max(0, Math.min(e.clientX - rect.left, rect.width)) : 
                        (e.changedTouches ? Math.max(0, Math.min(e.changedTouches[0].clientX - rect.left, rect.width)) : 0);
            const percentage = x / rect.width;
            
            if (player && player.getDuration) {
                const duration = player.getDuration();
                const newTime = duration * percentage;
                
                // Seek to the dropped position
                player.seekTo(newTime, true);
                
                // Update progress bar with animation
                videoProgressBar.style.transition = 'width 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
                videoProgressBar.style.width = (percentage * 100) + '%';
                setTimeout(() => {
                    videoProgressBar.style.transition = 'width 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                }, 300);
                
                updateTimeDisplay(newTime, duration);
                
                // Show status icon for seek
                showStatusIcon('bi-play-fill');
            }
            
            // Reset states
            isDraggingScrubber = false;
            scrubberDot.style.cursor = 'grab';
            
            setTimeout(() => {
                progressArea.classList.remove('dragging');
            }, 300);
            
        } else if (isDragging) {
            // Finalize regular drag
            if (e.clientX) {
                updateProgressFromEvent(e);
            } else if (e.changedTouches) {
                updateProgressFromTouch(e);
            }
            isDragging = false;
            progressArea.classList.remove('dragging');
        }
    }

    function updateProgressFromEvent(e) {
        const rect = progressArea.getBoundingClientRect();
        const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
        const percentage = x / rect.width;
        
        if (player && player.getDuration) {
            const duration = player.getDuration();
            const newTime = duration * percentage;
            
            player.seekTo(newTime, true);
            videoProgressBar.style.width = (percentage * 100) + '%';
            updateTimeDisplay(newTime, duration);
        }
    }

    function updateProgressFromTouch(e) {
        const rect = progressArea.getBoundingClientRect();
        const x = Math.max(0, Math.min(e.touches[0].clientX - rect.left, rect.width));
        const percentage = x / rect.width;
        
        if (player && player.getDuration) {
            const duration = player.getDuration();
            const newTime = duration * percentage;
            
            player.seekTo(newTime, true);
            videoProgressBar.style.width = (percentage * 100) + '%';
            updateTimeDisplay(newTime, duration);
        }
    }

    function handleHoverPreview(e) {
        if (isDragging || isDraggingScrubber) return;
        
        const rect = progressArea.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const percentage = Math.max(0, Math.min(1, x / rect.width));
        
        if (player && player.getDuration) {
            const duration = player.getDuration();
            const previewTimeValue = duration * percentage;
            
            // Update preview time display
            previewTime.textContent = formatTime(previewTimeValue);
            
            // Show preview with correct positioning
            const previewX = Math.max(80, Math.min(x, rect.width - 80));
            hoverPreview.style.left = previewX + 'px';
            hoverPreview.style.display = 'block';
            setTimeout(() => {
                hoverPreview.classList.add('visible');
            }, 10);
            
            // Update thumbnail preview
            updateThumbnailPreview(previewTimeValue);
        }
    }

    function updateThumbnailPreview(time) {
        // Try multiple YouTube thumbnail formats
        const thumbnailUrls = [
            `https://img.youtube.com/vi/${youtubeId}/0.jpg`,
            `https://img.youtube.com/vi/${youtubeId}/1.jpg`,
            `https://img.youtube.com/vi/${youtubeId}/2.jpg`,
            `https://img.youtube.com/vi/${youtubeId}/3.jpg`,
            `https://img.youtube.com/vi/${youtubeId}/mqdefault.jpg`,
            `https://img.youtube.com/vi/${youtubeId}/hqdefault.jpg`,
            `https://img.youtube.com/vi/${youtubeId}/sddefault.jpg`,
            `https://img.youtube.com/vi/${youtubeId}/maxresdefault.jpg`
        ];
        
        loadThumbnail(thumbnailUrls);
    }

    function loadThumbnail(urls, index = 0) {
        if (index >= urls.length) {
            // If no thumbnail works, show placeholder
            hoverPreview.innerHTML = `<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#333;color:white;">
                <i class="bi bi-play-btn" style="font-size:2rem;"></i>
            </div>`;
            hoverPreview.appendChild(previewTime);
            return;
        }
        
        const img = new Image();
        img.onload = function() {
            hoverPreview.innerHTML = `<img src="${urls[index]}" alt="Preview">`;
            hoverPreview.appendChild(previewTime);
        };
        img.onerror = function() {
            // Try next thumbnail
            loadThumbnail(urls, index + 1);
        };
        img.src = urls[index];
        // Add cache busting parameter
        img.src += '?t=' + new Date().getTime();
    }

    function hideHoverPreview() {
        if (!isDragging && !isDraggingScrubber) {
            hoverPreview.classList.remove('visible');
            setTimeout(() => {
                hoverPreview.style.display = 'none';
            }, 200);
        }
    }

    function showVideoControls() {
        playerWrapper.classList.add('show-controls');
        clearTimeout(showControlsTimeout);
        
        showControlsTimeout = setTimeout(() => {
            if (!isDragging && !isDraggingScrubber) {
                playerWrapper.classList.remove('show-controls');
            }
        }, 3000);
    }

    function hideVideoControls() {
        if (!isDragging && !isDraggingScrubber) {
            playerWrapper.classList.remove('show-controls');
        }
    }

    function updateTimeDisplay(currentTime, duration) {
        if (timeDisplay) {
            timeDisplay.textContent = formatTime(currentTime) + ' / ' + formatTime(duration);
        }
    }

    function togglePlay() {
        const state = player.getPlayerState();
        if (state === YT.PlayerState.PLAYING) {
            player.pauseVideo();
            showStatusIcon('bi-pause-fill');
        } else {
            player.playVideo();
            showStatusIcon('bi-play-fill');
        }
    }

    function toggleMute() {
        if (player.isMuted()) { 
            player.unMute(); 
            muteBtn.innerHTML = '<i class="bi bi-volume-up-fill"></i>';
        } else { 
            player.mute(); 
            muteBtn.innerHTML = '<i class="bi bi-volume-mute-fill"></i>';
        }
    }

    function toggleFullscreen() {
        const el = document.getElementById('playerWrapper');
        if (!document.fullscreenElement) {
            el.requestFullscreen();
            setTimeout(() => {
                playerWrapper.classList.add('show-controls');
            }, 100);
        } else {
            document.exitFullscreen();
        }
    }

    function handleKeyboard(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        switch(e.code) {
            case 'Space':
            case 'KeyK':
                e.preventDefault();
                togglePlay();
                break;
            case 'ArrowRight':
            case 'KeyL':
                forward();
                break;
            case 'ArrowLeft':
            case 'KeyJ':
                rewind();
                break;
            case 'KeyF':
                toggleFullscreen();
                break;
            case 'KeyM':
                toggleMute();
                break;
        }
    }

    function updateTimer() {
        if (player && player.getDuration) {
            const cur = player.getCurrentTime();
            const dur = player.getDuration();
            const percentage = (cur / dur) * 100;
            
            // Update progress bar smoothly
            if (!isDraggingScrubber) {
                videoProgressBar.style.width = percentage + '%';
            }
            
            // Update time display
            updateTimeDisplay(cur, dur);
            
            // Update buffer progress
            if (player.getVideoLoadedFraction) {
                const bufferPercentage = player.getVideoLoadedFraction() * 100;
                bufferProgress.style.width = bufferPercentage + '%';
            }
        }
    }

    function formatTime(s) { 
        s = Math.round(s); 
        const hours = Math.floor(s / 3600);
        const minutes = Math.floor((s % 3600) / 60);
        const seconds = s % 60;
        
        if (hours > 0) {
            return `${hours}:${minutes < 10 ? '0' : ''}${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        }
        return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }

document.addEventListener('DOMContentLoaded', function() {

    
    
    const rewindVid = document.getElementById('rewind');
    const forwardVid = document.getElementById('forward');
    const settingsBtn = document.getElementById('settingsBtn');
    const muteBtn = document.getElementById('muteBtn');
    const fullScreen = document.getElementById('fullScreen');

    rewindVid.addEventListener('click',rewind);
    forwardVid.addEventListener('click', forward);
    singleDouble.addEventListener('click', handleSingleTap);
    singleDouble.addEventListener('dblclick', handleDoubleTap)
    settingsBtn.addEventListener('click',toggleQualityMenu);
    muteBtn.addEventListener('click', toggleMute);
    fullScreen.addEventListener('click', toggleFullscreen);
    
    function handleSingleTap(e) {
        if (clickTimer) {
            clearTimeout(clickTimer);
            clickTimer = null;
        } else {
            clickTimer = setTimeout(() => {
                togglePlay();
                clickTimer = null;
            }, 250);
        }
    }

    function handleDoubleTap(e) {
        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        if (x < rect.width / 2) {
            rewind();
        } else {
            forward();
        }
    }

    document.querySelectorAll('.showMoreLess').forEach(button => {
        button.addEventListener('click', function() {
            const videoId = this.getAttribute('data-id');
            toggleDesc(videoId, this);
        });
    });

    // 3. Keyboard Controls
    

    function forward() { 
        player.seekTo(player.getCurrentTime() + 10, true); 
        showStatusIcon('bi-fast-forward-fill'); 
    }

    function rewind() { 
        player.seekTo(player.getCurrentTime() - 10, true); 
        showStatusIcon('bi-rewind-fill'); 
    }

    function showStatusIcon(iconClass) {
        statusIcon.className = `bi ${iconClass} center-icon show-icon`;
        setTimeout(() => statusIcon.classList.remove('show-icon'), 500);
    }

    function toggleQualityMenu() {
        qualityMenu.style.display = qualityMenu.style.display === 'block' ? 'none' : 'block';
        
        if(qualityMenu.style.display === 'block') {
            const levels = player.getAvailableQualityLevels();
            const currentQuality = player.getPlaybackQuality();
            
            const qualityLabels = {
                'highres': '4K',
                'hd2160': '2160p (4K)',
                'hd1440': '1440p (HD)',
                'hd1080': '1080p (HD)',
                'hd720': '720p (HD)',
                'large': '480p',
                'medium': '360p',
                'small': '240p',
                'tiny': '144p',
                'auto': 'Auto'
            };

            qualityMenu.innerHTML = '<div style="padding: 8px 15px; font-size: 0.75rem; color: #888; border-bottom: 1px solid #444; font-weight: bold;">Quality</div>';
            
            levels.reverse().forEach(level => {
                const item = document.createElement('div');
                item.className = 'quality-item';
                if (level === currentQuality) item.classList.add('active');
                
                item.innerText = qualityLabels[level] || level.toUpperCase();
                
                item.onclick = () => {
                    player.setPlaybackQuality(level);
                    const now = player.getCurrentTime();
                    player.seekTo(now, true); 
                    qualityMenu.style.display = 'none';
                };
                qualityMenu.appendChild(item);
            });
        }
    }

    window.onclick = function(event) {
        if (!event.target.matches('.bi-gear-fill') && !event.target.matches('.btn-ctrl')) {
            qualityMenu.style.display = 'none';
        }
    }
    
    // Handle responsive quality menu on mobile
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 480 && qualityMenu.style.display === 'block') {
            qualityMenu.style.display = 'none';
        }
    });
    
    // Fullscreen change listener
    document.addEventListener('fullscreenchange', function() {
        if (document.fullscreenElement) {
            playerWrapper.classList.add('show-controls');
        }
    });

    function toggleDesc(id, el) {
        const desc = document.getElementById(`desc-${id}`);
        
        if (!desc) {
            console.error('Description element not found');
            return;
        }
        
        // Toggle the expanded class
        desc.classList.toggle("expanded");
        
        // Update the button text
        if (desc.classList.contains("expanded")) {
            el.textContent = "Show less";
        } else {
            el.textContent = "Show more";
        }
    }
});