class PageLoader {
    constructor() {
        this.overlay = null;
        this.activeLoaders = 0; // Track multiple simultaneous operations
        this.init();
    }

    init() {
        // Create overlay if it doesn't exist
        if (!document.getElementById('global-loader-overlay')) {
            if (!this.overlay) {
                this.overlay = document.createElement('div');
                this.overlay.id = 'global-loader-overlay';
                this.overlay.innerHTML = `
                <div class="loader-container">
                    <div class="spinner-wrapper">
                        <div class="spinner"></div>
                        <div class="pulse-ring"></div>
                    </div>
                    <div class="loader-message">Processing...</div>
                    <div class="loader-submessage">Please don't close or refresh the page</div>
                </div>
                `;
                document.body.appendChild(this.overlay);

                this.addStyles();
            }
        }
    }

    addStyles() {
        if (!document.getElementById('loader-styles')) {
            const style = document.createElement('style');
            style.id = 'loader-styles';
            style.textContent = `
                #global-loader-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: var(--srch-bg-color);
                    backdrop-filter: blur(8px);
                    z-index: 999999;
                    display: none;
                    justify-content: center;
                    align-items: center;
                    transition: all 0.3s ease;
                }

                #global-loader-overlay.active {
                    display: flex;
                }


                .loader-container {
                    text-align: center;
                    color: white;
                    padding: 30px;
                    border-radius: 20px;
                    background: rgba(255, 255, 255, 0.1);
                    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
                    animation: fadeInUp 0.5s ease;
                }

                .spinner-wrapper {
                    position: relative;
                    width: 80px;
                    height: 80px;
                    margin: 0 auto 25px;
                }

                .spinner {
                    width: 80px;
                    height: 80px;
                    border: 5px solid rgba(255, 255, 255, 0.2);
                    border-top: 5px solid #fff;
                    border-right: 5px solid #4CAF50;
                    border-radius: 50%;
                    animation: spin 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
                    box-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
                }

                .pulse-ring {
                    position: absolute;
                    top: -15px;
                    left: -15px;
                    right: -15px;
                    bottom: -15px;
                    border: 2px solid rgba(76, 175, 80, 0.3);
                    border-radius: 50%;
                    animation: pulse 2s ease-out infinite;
                }

                .loader-message {
                    font-size: 1.5rem;
                    font-weight: 600;
                    margin-bottom: 10px;
                    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
                    background: linear-gradient(45deg, #fff, #4CAF50);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }

                .loader-submessage {
                    font-size: 0.95rem;
                    opacity: 0.8;
                    color: #ccc;
                    animation: fadeInOut 2s ease-in-out infinite;
                }

                /* Disable all clicks globally when overlay is active */
                body.loader-active *:not(#global-loader-overlay):not(#global-loader-overlay *) {
                    pointer-events: none !important;
                }

                /* Prevent scrolling when overlay is active */
                body.loader-active {
                    overflow: hidden !important;
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                @keyframes pulse {
                    0% { transform: scale(0.8); opacity: 1; }
                    70% { transform: scale(1.3); opacity: 0; }
                    100% { transform: scale(0.8); opacity: 0; }
                }

                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                @keyframes fadeInOut {
                    0%, 100% { opacity: 0.6; }
                    50% { opacity: 1; }
                }

                /* Progress bar for long operations */
                .progress-bar {
                    width: 100%;
                    height: 4px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 4px;
                    margin-top: 20px;
                    overflow: hidden;
                }

                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #4CAF50, #2196F3);
                    width: 0%;
                    transition: width 0.3s ease;
                }

                /* Different loader types */
                #global-loader-overlay.upload .loader-message {
                    background: linear-gradient(45deg, #fff, #2196F3);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }

                #global-loader-overlay.registration .loader-message {
                    background: linear-gradient(45deg, #fff, #FF9800);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
            `;
            document.head.appendChild(style);
        }
    }

    show(options = {}) {
        const {
            message = 'Processing...',
            submessage = 'Please don\'t close or refresh the page',
            type = 'default', // 'upload', 'registration', 'default'
            showProgress = false,
            progress = 0
        } = options;

        this.activeLoaders++;
        
        // Clear existing classes
        this.overlay.className = '';
        
        // Add type class
        if (type) {
            this.overlay.classList.add(type);
        }
        
        // Update messages
        const messageEl = this.overlay.querySelector('.loader-message');
        const submessageEl = this.overlay.querySelector('.loader-submessage');
        
        if (messageEl) messageEl.textContent = message;
        if (submessageEl) submessageEl.textContent = submessage;
        
        // Handle progress bar
        let progressBar = this.overlay.querySelector('.progress-bar');
        if (showProgress) {
            if (!progressBar) {
                progressBar = document.createElement('div');
                progressBar.className = 'progress-bar';
                progressBar.innerHTML = '<div class="progress-fill"></div>';
                this.overlay.querySelector('.loader-container').appendChild(progressBar);
            }
            const fill = progressBar.querySelector('.progress-fill');
            if (fill) fill.style.width = `${progress}%`;
        } else if (progressBar) {
            progressBar.remove();
        }
        
        // Show overlay
        this.overlay.classList.add('active');
        document.body.classList.add('loader-active');
        
        // Disable all buttons and links
        this.disableInteractiveElements(true);
    }

    hide() {
        this.activeLoaders = Math.max(0, this.activeLoaders - 1);
        
        if (this.activeLoaders === 0) {
            this.overlay.classList.remove('active');
            document.body.classList.remove('loader-active');
            
            // Re-enable all buttons and links
            this.disableInteractiveElements(false);
        }
    }

    disableInteractiveElements(disable) {
        const elements = document.querySelectorAll('button, a, input, select, textarea, [role="button"]');
        elements.forEach(el => {
            if (disable) {
                if (!el.hasAttribute('data-original-disabled')) {
                    if (el.disabled !== undefined) {
                        el.setAttribute('data-original-disabled', el.disabled);
                        el.disabled = true;
                    }
                }
            } else {
                if (el.hasAttribute('data-original-disabled')) {
                    el.disabled = el.getAttribute('data-original-disabled') === 'true';
                    el.removeAttribute('data-original-disabled');
                }
            }
        });
    }

    updateProgress(progress, message = null) {
        const progressBar = this.overlay.querySelector('.progress-bar');
        if (progressBar) {
            const fill = progressBar.querySelector('.progress-fill');
            if (fill) fill.style.width = `${progress}%`;
        }
        
        if (message) {
            const messageEl = this.overlay.querySelector('.loader-message');
            if (messageEl) messageEl.textContent = message;
        }
    }

    forceHide() {
        this.activeLoaders = 0;
        this.hide();
    }
}

// Create global instance
window.pageLoader = new PageLoader();