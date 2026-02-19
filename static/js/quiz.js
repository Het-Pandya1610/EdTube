const form = document.getElementById('quizForm');
const submitBtn = document.getElementById('submitBtn');

form.addEventListener('submit', () => {
    // Disable the button immediately
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spinning"></i> Submitting...';
});