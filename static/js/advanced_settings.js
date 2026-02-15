const textarea = document.getElementById("bioTextarea");
const counter = document.getElementById("bioCount");
const maxChars = 1000;

function updateBioCounter() {
    const length = textarea.value.length;
    counter.innerText = length;

    // Optional warning color
    if (length > maxChars * 0.9) {
        counter.style.color = "red";
    } else {
        counter.style.color = "";
    }
}

textarea?.addEventListener("input", updateBioCounter);
updateBioCounter();


document.addEventListener("DOMContentLoaded", function () {
    
    // Get data from the hidden element
    const userData = document.getElementById('user-data');
    
    if (!userData) {
        console.error('User data element not found');
        return;
    }
    
    // Extract data from dataset
    const CHECK_USERNAME_URL = userData.dataset.checkUrl;
    const SUGGEST_USERNAME_URL = userData.dataset.suggestUrl;
    const USER_FIRST_NAME = userData.dataset.firstName || '';
    const USER_LAST_NAME = userData.dataset.lastName || '';
    const USER_USERNAME = userData.dataset.username || '';
    
    console.log('Data loaded:', { 
        CHECK_USERNAME_URL, 
        SUGGEST_USERNAME_URL,
        USER_FIRST_NAME,
        USER_LAST_NAME,
        USER_USERNAME 
    });

    const usernameInput = document.getElementById("new_username");
    const checkBtn = document.getElementById("checkUsernameBtn");
    const suggestBtn = document.getElementById("suggestUsernameBtn");
    const updateBtn = document.getElementById("updateUsernameBtn");
    const feedback = document.getElementById("usernameFeedback");
    const suggestionsContainer = document.getElementById("suggestionsContainer");

    const nameFormat = document.getElementById("display_name_format");
    const previewName = document.getElementById("previewName");

    let usernameValid = false;
    let currentUsername = usernameInput?.value.trim() || '';

    // ===============================
    // EVENT DELEGATION FOR SUGGESTION BUTTONS
    // ===============================
    
    // Handle clicks on suggestion buttons (both initial and dynamically added)
    document.addEventListener('click', function(event) {
        const suggestionBtn = event.target.closest('.suggestion-btn');
        if (!suggestionBtn) return;
        
        // Get username from data attribute
        const username = suggestionBtn.dataset.username;
        if (username && usernameInput) {
            usernameInput.value = username;
            
            // Trigger username check
            setTimeout(() => checkBtn?.click(), 100);
        }
    });

    // ===============================
    // USERNAME AVAILABILITY CHECK
    // ===============================
    checkBtn?.addEventListener("click", async () => {
        
        if (!CHECK_USERNAME_URL) {
            console.error('CHECK_USERNAME_URL is not defined');
            feedback.innerHTML = "Configuration error. Please refresh the page.";
            feedback.className = "username-feedback error";
            return;
        }

        const username = usernameInput.value.trim();

        if (!username) {
            feedback.innerHTML = "Please enter a username";
            feedback.className = "username-feedback error";
            return;
        }

        if (username.length < 3) {
            feedback.innerHTML = "Username must be at least 3 characters";
            feedback.className = "username-feedback error";
            return;
        }

        if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            feedback.innerHTML = "Username can only contain letters, numbers, and underscores";
            feedback.className = "username-feedback error";
            return;
        }

        feedback.innerHTML = "Checking...";
        feedback.className = "username-feedback checking";

        try {
            const response = await fetch(`${CHECK_USERNAME_URL}?username=${encodeURIComponent(username)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();

            if (data.available) {
                feedback.innerHTML = "✅ Username available";
                feedback.className = "username-feedback feedback-available";
                usernameValid = true;
                updateBtn.disabled = false;
                
                // Clear suggestions when username is available
                if (suggestionsContainer) {
                    suggestionsContainer.innerHTML = '';
                }
            } else {
                if (data.is_current) {
                    feedback.innerHTML = "ℹ️ This is your current username";
                    feedback.className = "username-feedback info";
                    usernameValid = true;
                    updateBtn.disabled = false;
                    
                    // Clear suggestions
                    if (suggestionsContainer) {
                        suggestionsContainer.innerHTML = '';
                    }
                } else {
                    feedback.innerHTML = "❌ Username already taken";
                    feedback.className = "username-feedback feedback-taken";
                    usernameValid = false;
                    updateBtn.disabled = true;
                    
                    // Show suggestions if available
                    if (data.suggestions && data.suggestions.length > 0 && suggestionsContainer) {
                        let suggestionsHtml = '<p class="suggestions-title">Suggested usernames:</p>';
                        suggestionsHtml += '<div class="suggestions-list">';
                        data.suggestions.forEach(suggestion => {
                            suggestionsHtml += `<button type="button" class="suggestion-btn" data-username="${suggestion}">@${suggestion}</button>`;
                        });
                        suggestionsHtml += '</div>';
                        suggestionsContainer.innerHTML = suggestionsHtml;
                    }
                }
            }
        } catch (error) {
            console.error('Error checking username:', error);
            feedback.innerHTML = "Error checking username. Please try again.";
            feedback.className = "username-feedback error";
        }
    });

    // ===============================
    // SUGGEST USERNAMES
    // ===============================
    suggestBtn?.addEventListener("click", async () => {
        
        if (!SUGGEST_USERNAME_URL) {
            console.error('SUGGEST_USERNAME_URL is not defined');
            feedback.innerHTML = "Configuration error. Please refresh the page.";
            feedback.className = "username-feedback error";
            return;
        }

        feedback.innerHTML = "Generating suggestions...";
        feedback.className = "username-feedback checking";

        try {
            const response = await fetch(SUGGEST_USERNAME_URL);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();

            // Display suggestions directly in the container
            if (suggestionsContainer) {
                if (data.suggestions && data.suggestions.length > 0) {
                    let suggestionsHtml = '<p class="suggestions-title">Suggested usernames:</p>';
                    suggestionsHtml += '<div class="suggestions-list">';
                    data.suggestions.forEach(name => {
                        suggestionsHtml += `<button type="button" class="suggestion-btn" data-username="${name}">@${name}</button>`;
                    });
                    suggestionsHtml += '</div>';
                    suggestionsContainer.innerHTML = suggestionsHtml;
                } else {
                    suggestionsContainer.innerHTML = '<p class="suggestions-title">No suggestions available</p>';
                }
            }
            
            feedback.innerHTML = "";
        } catch (error) {
            console.error('Error getting suggestions:', error);
            feedback.innerHTML = "Error generating suggestions";
            feedback.className = "username-feedback error";
        }
    });

    // ===============================
    // REAL-TIME VALIDATION
    // ===============================
    usernameInput?.addEventListener("input", function() {
        const username = this.value.trim();
        
        if (username !== currentUsername) {
            usernameValid = false;
            updateBtn.disabled = true;
            feedback.innerHTML = "";
            
            // Restore initial suggestions if any
            const initialSuggestions = document.getElementById('initialSuggestionsList');
            if (initialSuggestions && suggestionsContainer) {
                suggestionsContainer.innerHTML = initialSuggestions.outerHTML;
            }
        }
    });

    // ===============================
    // DISABLE BUTTON ON SUBMIT
    // ===============================
    const usernameForm = document.getElementById("usernameForm");
    if (usernameForm) {
        usernameForm.addEventListener("submit", function(event) {
            if (!usernameValid) {
                event.preventDefault();
                feedback.innerHTML = "Please check username availability first";
                feedback.className = "username-feedback error";
            } else {
                updateBtn.disabled = true;
                updateBtn.style.opacity = "0.7";
                updateBtn.innerText = "Updating...";
            }
        });
    }

    // ===============================
    // LIVE NAME PREVIEW
    // ===============================
    function updateNamePreview() {
        if (!nameFormat || !previewName) return;
        
        const first = USER_FIRST_NAME || "User";
        const last = USER_LAST_NAME || "";
        const username = USER_USERNAME;

        let formatted = "";

        switch (nameFormat.value) {
            case "full":
                formatted = last ? `${first} ${last}` : first;
                break;

            case "first_last":
                formatted = last ? `${first} ${last.charAt(0)}.` : first;
                break;

            case "first_only":
                formatted = first;
                break;

            case "last_only":
                formatted = last || first;
                break;

            case "username":
                formatted = "@" + username;
                break;

            default:
                formatted = last ? `${first} ${last}` : first;
        }

        previewName.innerText = formatted;
    }

    nameFormat?.addEventListener("change", updateNamePreview);
    
    if (nameFormat && previewName) {
        updateNamePreview();
    }

});