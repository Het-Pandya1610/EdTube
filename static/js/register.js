// register.js - Updated with global page loader

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
const btn = document.getElementById("registerBtn");
    const passwordInput = document.getElementById("password"); // Changed to match your HTML
    const confirmInput = document.getElementById("confirm_password"); // Changed to match your HTML
    
    // Make sure pageLoader is available
    if (typeof pageLoader === 'undefined') {
        console.error('PageLoader not found. Make sure loader.js is loaded first.');
        return;
    }

    let isSubmitting = false;

    // Password strength indicator
    if (passwordInput) {
        // Create strength indicator element
        createStrengthIndicator();
        
        passwordInput.addEventListener('input', function() {
            updatePasswordStrength(this.value);
            
            // Check password match if confirm field has value
            if (confirmInput && confirmInput.value) {
                checkPasswordMatch();
            }
        });
    }

    // Password match checker
    if (confirmInput) {
        // Create match indicator element
        createMatchIndicator();
        
        confirmInput.addEventListener('input', checkPasswordMatch);
    }

    // Initialize password toggle eye icons
    initPasswordToggles();

    // Form validation
    function validateForm() {
        const fullname = document.querySelector('[name="fullname"]')?.value;
        const email = document.querySelector('[name="email"]')?.value;
        const role = document.getElementById('role')?.value;
        const password = passwordInput?.value || '';
        const confirm = confirmInput?.value || '';
        
        // Check username
        if (!fullname || fullname.trim() === '') {
            showNotification('Fullname is required', 'error');
            return false;
        }
        
        // Check email
        if (!email || email.trim() === '') {
            showNotification('Email is required', 'error');
            return false;
        }
        
        // Validate email format
        if (!validateEmail(email)) {
            showNotification('Please enter a valid email address', 'error');
            return false;
        }
        
        // Check password
        if (!password) {
            showNotification('Password is required', 'error');
            return false;
        }
        
        // Check password length
        if (password.length < 8) {
            showNotification('Password must be at least 8 characters long', 'error');
            return false;
        }
        
        // Check if passwords match
        if (password !== confirm) {
            showNotification('Passwords do not match!', 'error');
            return false;
        }
        
        // Check if role is selected
        if (!role || role === '') {
            showNotification('Please select a role (Student or Teacher)', 'error');
            return false;
        }
        
        return true;
    }

    // Email validation helper
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // Form submit handler
    form.addEventListener("submit", async function (e) {
        // Prevent double submission
         e.preventDefault();
        if (isSubmitting) {
            return;
        }

        // Validate form first
        if (!validateForm()) {
            return;
        }

        isSubmitting = true;

        // Disable button
        btn.disabled = true;
        btn.innerText = "Creating Account...";
        btn.style.opacity = "0.7";
        btn.style.cursor = "not-allowed";

        // Use global page loader
        pageLoader.show({
            message: 'Creating your account...',
            submessage: 'Please wait while we set up your profile',
            type: 'registration',
            showProgress: true
        });

        try {
        // Collect form data
            const formData = new FormData(form);
            
            // Send AJAX request
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                pageLoader.updateProgress(100, 'Account created successfully!');
                
                // Redirect after success
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/login/';
                }, 1500);
            } else {
                throw new Error(data.message || data.error || 'Registration failed');
            }

        } catch (error) {
            console.error('Registration error:', error);
            
            // Hide loader
            pageLoader.hide();
            
            // Show error message
            showNotification(error.message, 'error');
            
            // Reset button
            btn.disabled = false;
            btn.innerText = "Register";
            btn.style.opacity = "1";
            btn.style.cursor = "pointer";
            
            isSubmitting = false;
        }
    });

    // Prevent accidental navigation during registration
    window.addEventListener('beforeunload', function (event) {
        if (isSubmitting) {
            event.preventDefault();
            event.returnValue = 'Registration in progress. Are you sure you want to leave?';
            return event.returnValue;
        }
    });
});

function getCsrfToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}

// Create password strength indicator
function createStrengthIndicator() {
    // Check if indicator already exists
    if (document.getElementById('password-strength-container')) return;
    
    const passwordField = document.getElementById('password');
    if (!passwordField) return;
    
    // Create container
    const container = document.createElement('div');
    container.id = 'password-strength-container';
    container.className = 'password-strength-container';
    container.style.marginTop = '8px';
    container.style.marginBottom = '12px';
    
    // Create strength meter
    container.innerHTML = `
        <div class="strength-meter">
            <div class="strength-meter-bar" id="password-strength-bar"></div>
        </div>
        <div class="strength-labels">
            <span id="strength-text">Enter password</span>
            <span id="strength-score" class="strength-score"></span>
        </div>
        <div class="password-requirements" id="password-requirements">
            <div class="requirement" id="req-length">
                <i class="bi bi-x-circle"></i>
                <span>At least 8 characters</span>
            </div>
            <div class="requirement" id="req-uppercase">
                <i class="bi bi-x-circle"></i>
                <span>At least one uppercase letter</span>
            </div>
            <div class="requirement" id="req-lowercase">
                <i class="bi bi-x-circle"></i>
                <span>At least one lowercase letter</span>
            </div>
            <div class="requirement" id="req-number">
                <i class="bi bi-x-circle"></i>
                <span>At least one number</span>
            </div>
            <div class="requirement" id="req-special">
                <i class="bi bi-x-circle"></i>
                <span>At least one special character (!@#$%^&*)</span>
            </div>
        </div>
    `;
    
    // Insert after password field
    passwordField.parentNode.insertAdjacentElement('afterend', container);
    
    // Add CSS styles
    addStrengthStyles();
}

// Create password match indicator
function createMatchIndicator() {
    // Check if indicator already exists
    if (document.getElementById('password-match-container')) return;
    
    const confirmField = document.getElementById('confirm_password');
    if (!confirmField) return;
    
    // Create container
    const container = document.createElement('div');
    container.id = 'password-match-container';
    container.className = 'password-match-container';
    container.style.marginTop = '5px';
    container.style.marginBottom = '15px';
    container.style.display = 'none';
    
    container.innerHTML = `
        <div class="password-match" id="password-match">
            <i class="bi bi-check-circle-fill" id="match-icon"></i>
            <span id="match-message"></span>
        </div>
    `;
    
    // Insert after confirm field
    confirmField.parentNode.insertAdjacentElement('afterend', container);
}

// Add CSS styles for strength indicator
function addStrengthStyles() {
    if (document.getElementById('strength-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'strength-styles';
    style.textContent = `
        .password-strength-container {
            margin: 10px 0 15px 0;
            padding: 0 5px;
        }
        
        .strength-meter {
            height: 6px;
            background-color: rgba(128, 128, 128, 0.2);
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 8px;
        }
        
        .strength-meter-bar {
            height: 100%;
            width: 0%;
            border-radius: 10px;
            transition: width 0.3s ease, background-color 0.3s ease;
        }
        
        .strength-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--text-color, #333);
            opacity: 0.8;
            margin-bottom: 10px;
        }
        
        .strength-score {
            font-weight: bold;
        }
        
        .password-requirements {
            background-color: rgba(128, 128, 128, 0.05);
            border-radius: 8px;
            padding: 12px;
            border: 1px solid rgba(128, 128, 128, 0.2);
        }
        
        .requirement {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
            font-size: 0.85rem;
            color: #ff4444;
            transition: color 0.3s ease;
        }
        
        .requirement i {
            font-size: 1rem;
        }
        
        .requirement.met {
            color: #28a745;
        }
        
        .requirement.met i {
            color: #28a745;
        }
        
        .password-match-container {
            margin: 5px 0 15px 0;
            padding: 0 5px;
        }
        
        .password-match {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
            padding: 8px 12px;
            border-radius: 6px;
            background-color: rgba(128, 128, 128, 0.05);
        }
        
        .password-match.match {
            color: #28a745;
            background-color: rgba(40, 167, 69, 0.1);
        }
        
        .password-match.match i {
            color: #28a745;
        }
        
        .password-match.no-match {
            color: #dc3545;
            background-color: rgba(220, 53, 69, 0.1);
        }
        
        .password-match.no-match i {
            color: #dc3545;
        }
        
        .strength-0 .strength-meter-bar { background-color: #ff4444; width: 0%; }
        .strength-1 .strength-meter-bar { background-color: #ff7744; width: 20%; }
        .strength-2 .strength-meter-bar { background-color: #ffaa44; width: 40%; }
        .strength-3 .strength-meter-bar { background-color: #ffdd44; width: 60%; }
        .strength-4 .strength-meter-bar { background-color: #44ff44; width: 80%; }
        .strength-5 .strength-meter-bar { background-color: #008e00; width: 100%; }
    `;
    
    document.head.appendChild(style);
}

// Password strength update function
function updatePasswordStrength(password) {
    // Define criteria
    const criteria = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        numbers: /[0-9]/.test(password),
        special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)
    };
    
    // Calculate strength (0-4)
    const strength = Object.values(criteria).filter(Boolean).length;
    
    // Update strength bar
    const strengthBar = document.getElementById('password-strength-bar');
    const container = document.querySelector('.password-strength-container');
    const strengthText = document.getElementById('strength-text');
    const strengthScore = document.getElementById('strength-score');
    
    if (strengthBar && container) {
        // Remove existing strength classes
        container.classList.remove('strength-0', 'strength-1', 'strength-2', 'strength-3', 'strength-4', 'strength-5');
        
        // Add new strength class
        container.classList.add(`strength-${strength}`);
        
        // Update text
        const labels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
        if (strengthText) {
            strengthText.textContent = labels[strength] || 'Enter password';
        }
        
        if (strengthScore) {
            strengthScore.textContent = `${strength}/5`;
        }
    }
    
    // Update requirement icons
    updateRequirement('req-length', criteria.length);
    updateRequirement('req-uppercase', criteria.uppercase);
    updateRequirement('req-lowercase', criteria.lowercase);
    updateRequirement('req-number', criteria.numbers);
    updateRequirement('req-special', criteria.special);
}

function updateRequirement(elementId, isMet) {
    const reqElement = document.getElementById(elementId);
    if (reqElement) {
        if (isMet) {
            reqElement.classList.add('met');
            const icon = reqElement.querySelector('i');
            if (icon) {
                icon.classList.remove('bi-x-circle');
                icon.classList.add('bi-check-circle-fill');
            }
        } else {
            reqElement.classList.remove('met');
            const icon = reqElement.querySelector('i');
            if (icon) {
                icon.classList.remove('bi-check-circle-fill');
                icon.classList.add('bi-x-circle');
            }
        }
    }
}

function checkPasswordMatch() {
    const password = document.getElementById('password')?.value || '';
    const confirm = document.getElementById('confirm_password')?.value || '';
    const matchContainer = document.getElementById('password-match-container');
    const matchElement = document.getElementById('password-match');
    
    if (matchContainer && matchElement) {
        const icon = document.getElementById('match-icon');
        const message = document.getElementById('match-message');
        
        if (confirm === '') {
            matchContainer.style.display = 'none';
        } else if (password === confirm) {
            matchContainer.style.display = 'block';
            matchElement.className = 'password-match match';
            icon.className = 'bi bi-check-circle-fill';
            message.textContent = 'Passwords match';
        } else {
            matchContainer.style.display = 'block';
            matchElement.className = 'password-match no-match';
            icon.className = 'bi bi-exclamation-circle-fill';
            message.textContent = 'Passwords do not match';
        }
    }
}

// Helper function for notifications
function showNotification(message, type = 'info') {
    // Use your existing showNotification function if available
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
    } else {
        // Create a simple notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4caf50' : '#2196f3'};
            color: white;
            border-radius: 5px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}