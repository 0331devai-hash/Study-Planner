/**
 * StudyPlanner Main Client-Side JavaScript
 * Handles navigation toggling, flash message dismissal, CSRF helpers, and UI interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavbarToggle();
    initFlashAutoDismiss();
});

/**
 * Mobile navigation menu toggle handler.
 */
function initNavbarToggle() {
    const toggleBtn = document.getElementById('navbar-toggle');
    const menu = document.getElementById('navbar-menu');

    if (toggleBtn && menu) {
        toggleBtn.addEventListener('click', () => {
            menu.classList.toggle('show');
        });
    }
}

/**
 * Automatically dismiss success and info flash messages after 5 seconds.
 */
function initFlashAutoDismiss() {
    const alerts = document.querySelectorAll('.alert-success, .alert-info');
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
}

/**
 * Confirmation dialog for task deletion.
 * @param {string} taskTitle - Title of task to be deleted.
 * @returns {boolean}
 */
function confirmDeleteTask(taskTitle) {
    return confirm(`Are you sure you want to delete "${taskTitle}"?\nThis action cannot be undone.`);
}

/**
 * Helper to retrieve CSRF token from page meta tag.
 * @returns {string} CSRF token
 */
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}
