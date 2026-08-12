/**
 * StudyPlanner Form Validation Helper
 * Provides instant real-time client-side input validation and error feedback styling.
 */

document.addEventListener('DOMContentLoaded', () => {
    initFormValidation();
});

function initFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');

    forms.forEach((form) => {
        form.addEventListener('submit', (event) => {
            let isValid = true;

            // Clear existing validation messages
            form.querySelectorAll('.is-invalid').forEach((el) => el.classList.remove('is-invalid'));

            // Email field validation
            const emailInput = form.querySelector('input[type="email"]');
            if (emailInput && emailInput.value.trim() !== '') {
                if (!validateEmail(emailInput.value.trim())) {
                    showFieldError(emailInput, 'Please enter a valid email address.');
                    isValid = false;
                }
            }

            // Password length & strength check
            const passwordInput = form.querySelector('#password');
            if (passwordInput && form.id === 'register-form') {
                if (passwordInput.value.length < 8) {
                    showFieldError(passwordInput, 'Password must be at least 8 characters long.');
                    isValid = false;
                }
            }

            // Password confirm check
            const confirmInput = form.querySelector('#confirm_password');
            if (passwordInput && confirmInput) {
                if (passwordInput.value !== confirmInput.value) {
                    showFieldError(confirmInput, 'Passwords do not match.');
                    isValid = false;
                }
            }

            if (!isValid) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
    });
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showFieldError(inputElement, message) {
    inputElement.classList.add('is-invalid');
    let feedback = inputElement.parentElement.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        inputElement.parentElement.appendChild(feedback);
    }
    feedback.textContent = message;
}
