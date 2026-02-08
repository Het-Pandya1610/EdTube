// static/js/cropper.js - UPDATED VERSION

class ImageCropper {
    constructor(options = {}) {
        this.options = {
            container: null,
            imageSrc: '',
            aspectRatio: null,
            onCrop: null,
            onCancel: null,
            cropType: 'default', // 'pfp' or 'banner' or 'default'
            ...options
        };
        
        this.isActive = false;
        this.cropper = null;
        this.cropArea = null;
        this.previewCanvas = null;
        this.init();
    }

    init() {
        if (!this.options.container) {
            console.error('Container element is required');
            return;
        }

        this.createModal();
        this.loadImage();
    }

    createModal() {
        this.modal = document.createElement('div');
        this.modal.className = 'cropper-modal';
        
        // Add rounded preview for profile pictures
        const previewHtml = this.options.cropType === 'pfp' ? `
            <div class="cropper-preview-sidebar">
                <div class="rounded-preview-container">
                    <h4>Preview</h4>
                    <div class="rounded-preview" id="rounded-preview">
                        <div class="rounded-preview-image" id="rounded-preview-image"></div>
                    </div>
                    <p class="preview-note">Your profile picture will appear as a circle</p>
                </div>
            </div>
        ` : '';
        
        this.modal.innerHTML = `
            <div class="cropper-modal-content ${this.options.cropType === 'pfp' ? 'with-sidebar' : ''}">
                <div class="cropper-header">
                    <h3>${this.getTitle()}</h3>
                    <button class="cropper-close">&times;</button>
                </div>
                <div class="cropper-body">
                    ${previewHtml}
                    <div class="cropper-main">
                        <div class="cropper-preview-container">
                            <div class="cropper-preview">
                                <img id="cropper-image" src="${this.options.imageSrc}" alt="Crop">
                            </div>
                        </div>
                        <div class="cropper-controls">
                            <div class="cropper-zoom">
                                <label>Zoom:</label>
                                <input type="range" id="cropper-zoom" min="0.1" max="3" step="0.1" value="1">
                            </div>
                            <div class="cropper-rotate">
                                <label>Rotate:</label>
                                <input type="range" id="cropper-rotate" min="-180" max="180" step="1" value="0">
                            </div>
                            <div class="cropper-presets">
                                ${this.options.cropType === 'pfp' ? '<button class="preset-btn active" data-aspect="1:1">Profile (1:1)</button>' : ''}
                                ${this.options.cropType === 'banner' ? '<button class="preset-btn active" data-aspect="16:9">Banner (16:9)</button>' : ''}
                                <button class="preset-btn" data-aspect="4:3">Standard (4:3)</button>
                                <button class="preset-btn" data-aspect="free">Free</button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="cropper-footer">
                    <button class="cropper-btn cancel">Cancel</button>
                    <button class="cropper-btn crop">Crop Image</button>
                </div>
            </div>
        `;

        document.body.appendChild(this.modal);
        this.bindEvents();
        this.isActive = true;
    }

    getTitle() {
        switch(this.options.cropType) {
            case 'pfp':
                return 'Crop Profile Picture';
            case 'banner':
                return 'Crop Banner';
            default:
                return 'Crop Image';
        }
    }

    loadImage() {
        const image = this.modal.querySelector('#cropper-image');
        image.onload = () => {
            this.initCropper();
            if (this.options.cropType === 'pfp') {
                this.initRoundedPreview();
            }
        };
        image.onerror = () => {
            console.error('Failed to load image');
            this.destroy();
        };
        image.src = this.options.imageSrc;
    }

    initRoundedPreview() {
        this.previewCanvas = document.createElement('canvas');
        this.previewCanvas.width = 200;
        this.previewCanvas.height = 200;
        
        const previewImage = this.modal.querySelector('#rounded-preview-image');
        previewImage.style.width = '200px';
        previewImage.style.height = '200px';
        
        // Update preview when crop area changes
        this.updateRoundedPreview();
    }

    updateRoundedPreview() {
        if (!this.previewCanvas || this.options.cropType !== 'pfp') return;
        
        const previewImage = this.modal.querySelector('#rounded-preview-image');
        if (!previewImage) return;
        
        // Create a temporary canvas to show rounded preview
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        
        tempCanvas.width = 200;
        tempCanvas.height = 200;
        
        // Clear canvas
        tempCtx.clearRect(0, 0, 200, 200);
        
        // Create circular clipping path
        tempCtx.beginPath();
        tempCtx.arc(100, 100, 100, 0, Math.PI * 2);
        tempCtx.closePath();
        tempCtx.clip();
        
        // Draw the current crop preview
        // For now, we'll use a placeholder - in production, you'd draw the actual cropped area
        tempCtx.fillStyle = '#4f46e5';
        tempCtx.fillRect(0, 0, 200, 200);
        
        // Convert to data URL and set as background
        previewImage.style.backgroundImage = `url(${tempCanvas.toDataURL()})`;
        previewImage.style.backgroundSize = 'cover';
        previewImage.style.backgroundPosition = 'center';
        previewImage.style.borderRadius = '50%';
    }

    initCropper() {
        const image = this.modal.querySelector('#cropper-image');
        const container = image.parentElement;
        
        this.cropper = {
            image: image,
            container: container,
            scale: 1,
            rotation: 0,
            cropArea: null,
            isDragging: false,
            startX: 0,
            startY: 0
        };

        this.createCropArea();
        
        // Update rounded preview when crop area changes
        if (this.options.cropType === 'pfp') {
            const updatePreview = () => {
                this.updateRoundedPreview();
            };
            
            // Watch for crop area changes
            const observer = new MutationObserver(updatePreview);
            observer.observe(this.cropArea, { attributes: true, attributeFilter: ['style'] });
        }
    }

    createCropArea() {
        const container = this.cropper.container;
        
        // Remove existing crop area
        const existingArea = container.querySelector('.crop-area');
        if (existingArea) existingArea.remove();

        this.cropArea = document.createElement('div');
        this.cropArea.className = 'crop-area';
        
        // Add rounded corners for profile pictures
        if (this.options.cropType === 'pfp') {
            this.cropArea.classList.add('rounded-crop');
        }
        
        // Set initial size based on aspect ratio
        const containerRect = container.getBoundingClientRect();
        const containerWidth = containerRect.width;
        const containerHeight = containerRect.height;
        
        let cropWidth, cropHeight;
        
        if (this.options.aspectRatio && this.options.aspectRatio !== 'free') {
            const [w, h] = this.options.aspectRatio.split(':').map(Number);
            const ratio = w / h;
            
            if (containerWidth / containerHeight > ratio) {
                cropHeight = containerHeight * 0.6;
                cropWidth = cropHeight * ratio;
            } else {
                cropWidth = containerWidth * 0.6;
                cropHeight = cropWidth / ratio;
            }
        } else {
            cropWidth = containerWidth * 0.6;
            cropHeight = containerHeight * 0.6;
        }
        
        // Ensure minimum size
        cropWidth = Math.max(100, cropWidth);
        cropHeight = Math.max(100, cropHeight);
        
        this.cropArea.style.width = `${cropWidth}px`;
        this.cropArea.style.height = `${cropHeight}px`;
        
        // Center the crop area
        const left = (containerWidth - cropWidth) / 2;
        const top = (containerHeight - cropHeight) / 2;
        
        this.cropArea.style.left = `${left}px`;
        this.cropArea.style.top = `${top}px`;
        
        container.appendChild(this.cropArea);
        
        // Add resize handles
        this.addResizeHandles();
        
        // Setup drag
        this.setupDrag();
    }

    addResizeHandles() {
        const positions = ['nw', 'ne', 'sw', 'se', 'n', 'e', 's', 'w'];
        
        positions.forEach(pos => {
            const handle = document.createElement('div');
            handle.className = `crop-handle ${pos}`;
            this.cropArea.appendChild(handle);
            
            this.setupResizeHandle(handle, pos);
        });
    }

    setupResizeHandle(handle, position) {
        const startResize = (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const startX = e.clientX || e.touches[0].clientX;
            const startY = e.clientY || e.touches[0].clientY;
            const startWidth = this.cropArea.offsetWidth;
            const startHeight = this.cropArea.offsetHeight;
            const startLeft = this.cropArea.offsetLeft;
            const startTop = this.cropArea.offsetTop;
            
            const onMouseMove = (moveEvent) => {
                const clientX = moveEvent.clientX || moveEvent.touches[0].clientX;
                const clientY = moveEvent.clientY || moveEvent.touches[0].clientY;
                
                const deltaX = clientX - startX;
                const deltaY = clientY - startY;
                
                let newWidth = startWidth;
                let newHeight = startHeight;
                let newLeft = startLeft;
                let newTop = startTop;
                
                // Handle different resize directions
                if (position.includes('e')) {
                    newWidth = startWidth + deltaX;
                }
                if (position.includes('w')) {
                    newWidth = startWidth - deltaX;
                    newLeft = startLeft + deltaX;
                }
                if (position.includes('s')) {
                    newHeight = startHeight + deltaY;
                }
                if (position.includes('n')) {
                    newHeight = startHeight - deltaY;
                    newTop = startTop + deltaY;
                }
                
                // Maintain aspect ratio if needed
                if (this.options.aspectRatio && this.options.aspectRatio !== 'free') {
                    const [w, h] = this.options.aspectRatio.split(':').map(Number);
                    const ratio = w / h;
                    
                    if (position.includes('e') || position.includes('w')) {
                        newHeight = newWidth / ratio;
                        if (position.includes('n')) {
                            newTop = startTop + (startHeight - newHeight);
                        }
                    } else if (position.includes('s') || position.includes('n')) {
                        newWidth = newHeight * ratio;
                        if (position.includes('w')) {
                            newLeft = startLeft + (startWidth - newWidth);
                        }
                    }
                }
                
                // Minimum size
                newWidth = Math.max(50, newWidth);
                newHeight = Math.max(50, newHeight);
                
                // Keep within bounds
                const maxLeft = this.cropper.container.offsetWidth - newWidth;
                const maxTop = this.cropper.container.offsetHeight - newHeight;
                
                newLeft = Math.max(0, Math.min(newLeft, maxLeft));
                newTop = Math.max(0, Math.min(newTop, maxTop));
                
                this.cropArea.style.width = `${newWidth}px`;
                this.cropArea.style.height = `${newHeight}px`;
                this.cropArea.style.left = `${newLeft}px`;
                this.cropArea.style.top = `${newTop}px`;
                
                // Update preview for profile pictures
                if (this.options.cropType === 'pfp') {
                    this.updateRoundedPreview();
                }
            };
            
            const onMouseUp = () => {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('touchmove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                document.removeEventListener('touchend', onMouseUp);
            };
            
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('touchmove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
            document.addEventListener('touchend', onMouseUp);
        };
        
        handle.addEventListener('mousedown', startResize);
        handle.addEventListener('touchstart', startResize);
    }

    setupDrag() {
        const startDrag = (e) => {
            e.preventDefault();
            this.cropper.isDragging = true;
            
            const clientX = e.clientX || e.touches[0].clientX;
            const clientY = e.clientY || e.touches[0].clientY;
            
            this.cropper.startX = clientX - this.cropArea.offsetLeft;
            this.cropper.startY = clientY - this.cropArea.offsetTop;
            
            const onMouseMove = (moveEvent) => {
                if (!this.cropper.isDragging) return;
                
                const moveX = moveEvent.clientX || moveEvent.touches[0].clientX;
                const moveY = moveEvent.clientY || moveEvent.touches[0].clientY;
                
                let newLeft = moveX - this.cropper.startX;
                let newTop = moveY - this.cropper.startY;
                
                // Keep within bounds
                const maxLeft = this.cropper.container.offsetWidth - this.cropArea.offsetWidth;
                const maxTop = this.cropper.container.offsetHeight - this.cropArea.offsetHeight;
                
                newLeft = Math.max(0, Math.min(newLeft, maxLeft));
                newTop = Math.max(0, Math.min(newTop, maxTop));
                
                this.cropArea.style.left = `${newLeft}px`;
                this.cropArea.style.top = `${newTop}px`;
                
                // Update preview for profile pictures
                if (this.options.cropType === 'pfp') {
                    this.updateRoundedPreview();
                }
            };
            
            const onMouseUp = () => {
                this.cropper.isDragging = false;
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('touchmove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                document.removeEventListener('touchend', onMouseUp);
            };
            
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('touchmove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
            document.addEventListener('touchend', onMouseUp);
        };
        
        this.cropArea.addEventListener('mousedown', startDrag);
        this.cropArea.addEventListener('touchstart', startDrag);
        
        // Prevent drag on resize handles
        this.cropArea.querySelectorAll('.crop-handle').forEach(handle => {
            handle.addEventListener('mousedown', (e) => {
                e.stopPropagation();
            });
        });
    }

    bindEvents() {
        // Close button
        this.modal.querySelector('.cropper-close').addEventListener('click', () => {
            if (this.options.onCancel) {
                this.options.onCancel();
            }
            this.destroy();
        });
        
        // Cancel button
        this.modal.querySelector('.cancel').addEventListener('click', () => {
            if (this.options.onCancel) {
                this.options.onCancel();
            }
            this.destroy();
        });
        
        // Crop button
        this.modal.querySelector('.crop').addEventListener('click', () => {
            this.cropImage();
        });
        
        // Zoom
        this.modal.querySelector('#cropper-zoom').addEventListener('input', (e) => {
            this.cropper.scale = parseFloat(e.target.value);
            this.cropper.image.style.transform = `scale(${this.cropper.scale}) rotate(${this.cropper.rotation}deg)`;
            
            // Update preview for profile pictures
            if (this.options.cropType === 'pfp') {
                this.updateRoundedPreview();
            }
        });
        
        // Rotate
        this.modal.querySelector('#cropper-rotate').addEventListener('input', (e) => {
            this.cropper.rotation = parseInt(e.target.value);
            this.cropper.image.style.transform = `scale(${this.cropper.scale}) rotate(${this.cropper.rotation}deg)`;
            
            // Update preview for profile pictures
            if (this.options.cropType === 'pfp') {
                this.updateRoundedPreview();
            }
        });
        
        // Aspect ratio presets
        this.modal.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Update active button
                this.modal.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                const aspect = e.target.dataset.aspect;
                this.options.aspectRatio = aspect === 'free' ? null : aspect;
                
                // Add/remove rounded corners for profile pictures
                if (this.options.cropType === 'pfp') {
                    if (aspect === '1:1') {
                        this.cropArea.classList.add('rounded-crop');
                    } else {
                        this.cropArea.classList.remove('rounded-crop');
                    }
                }
                
                this.createCropArea();
            });
        });
        
        // Close on outside click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                if (this.options.onCancel) {
                    this.options.onCancel();
                }
                this.destroy();
            }
        });
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isActive) {
                if (this.options.onCancel) {
                    this.options.onCancel();
                }
                this.destroy();
            }
        });
    }

    cropImage() {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Get crop coordinates relative to the image
        const containerRect = this.cropper.container.getBoundingClientRect();
        const cropRect = this.cropArea.getBoundingClientRect();
        const imageRect = this.cropper.image.getBoundingClientRect();
        
        // Calculate scale from displayed to actual
        const scaleX = this.cropper.image.naturalWidth / imageRect.width;
        const scaleY = this.cropper.image.naturalHeight / imageRect.height;
        
        // Crop coordinates relative to actual image
        const cropX = (cropRect.left - imageRect.left) * scaleX;
        const cropY = (cropRect.top - imageRect.top) * scaleY;
        const cropWidth = cropRect.width * scaleX;
        const cropHeight = cropRect.height * scaleY;
        
        // Set canvas dimensions
        canvas.width = cropWidth;
        canvas.height = cropHeight;
        
        // Handle rotation
        if (this.cropper.rotation !== 0) {
            // Create temporary canvas for rotation
            const tempCanvas = document.createElement('canvas');
            const tempCtx = tempCanvas.getContext('2d');
            
            tempCanvas.width = this.cropper.image.naturalWidth;
            tempCanvas.height = this.cropper.image.naturalHeight;
            
            // Clear and rotate
            tempCtx.clearRect(0, 0, tempCanvas.width, tempCanvas.height);
            tempCtx.save();
            tempCtx.translate(tempCanvas.width / 2, tempCanvas.height / 2);
            tempCtx.rotate(this.cropper.rotation * Math.PI / 180);
            tempCtx.drawImage(
                this.cropper.image,
                -this.cropper.image.naturalWidth / 2,
                -this.cropper.image.naturalHeight / 2
            );
            tempCtx.restore();
            
            // Draw cropped portion
            ctx.drawImage(tempCanvas, cropX, cropY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);
        } else {
            // Direct crop without rotation
            ctx.drawImage(this.cropper.image, cropX, cropY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);
        }
        
        // For profile pictures, create a circular mask
        if (this.options.cropType === 'pfp') {
            const roundedCanvas = document.createElement('canvas');
            const roundedCtx = roundedCanvas.getContext('2d');
            
            roundedCanvas.width = cropWidth;
            roundedCanvas.height = cropHeight;
            
            // Create circular clipping path
            roundedCtx.beginPath();
            roundedCtx.arc(cropWidth / 2, cropHeight / 2, Math.min(cropWidth, cropHeight) / 2, 0, Math.PI * 2);
            roundedCtx.closePath();
            roundedCtx.clip();
            
            // Draw the cropped image
            roundedCtx.drawImage(canvas, 0, 0);
            
            // Get the rounded image
            roundedCanvas.toBlob((blob) => {
                this.handleCroppedBlob(blob);
            }, 'image/png', 0.95);
        } else {
            // Get regular cropped image as blob
            canvas.toBlob((blob) => {
                this.handleCroppedBlob(blob);
            }, 'image/jpeg', 0.95);
        }
    }

    handleCroppedBlob(blob) {
        if (!blob) {
            console.error('Failed to create blob from canvas');
            return;
        }
        
        const croppedImageUrl = URL.createObjectURL(blob);
        
        if (this.options.onCrop) {
            this.options.onCrop(croppedImageUrl, blob);
        }
        
        this.destroy();
    }

    destroy() {
        if (this.modal && this.modal.parentNode) {
            this.modal.parentNode.removeChild(this.modal);
        }
        this.isActive = false;
    }
}

// Make it available globally
if (typeof window !== 'undefined') {
    window.ImageCropper = ImageCropper;
}