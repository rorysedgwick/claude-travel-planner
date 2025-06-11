/**
 * Travel Planner Frontend JavaScript Application
 * Provides utility functions for API communication and DOM manipulation
 */

// API Configuration
const API_BASE_URL = '/api';

// Utility Functions
const TravelPlanner = {
    /**
     * Make HTTP request to API endpoint
     * @param {string} endpoint - API endpoint (e.g., '/trips')
     * @param {Object} options - Request options (method, body, headers)
     * @returns {Promise<Object>} - API response
     */
    async apiRequest(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error?.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    },

    /**
     * GET request helper
     * @param {string} endpoint - API endpoint
     * @returns {Promise<Object>} - API response
     */
    async get(endpoint) {
        return this.apiRequest(endpoint, { method: 'GET' });
    },

    /**
     * POST request helper
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body data
     * @returns {Promise<Object>} - API response
     */
    async post(endpoint, data) {
        return this.apiRequest(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    /**
     * PUT request helper
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body data
     * @returns {Promise<Object>} - API response
     */
    async put(endpoint, data) {
        return this.apiRequest(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    /**
     * DELETE request helper
     * @param {string} endpoint - API endpoint
     * @returns {Promise<Object>} - API response
     */
    async delete(endpoint) {
        return this.apiRequest(endpoint, { method: 'DELETE' });
    },

    /**
     * Show loading state on element
     * @param {HTMLElement} element - Element to show loading state
     */
    showLoading(element) {
        element.classList.add('loading');
        const spinner = document.createElement('div');
        spinner.className = 'spinner-border spinner-border-sm me-2';
        spinner.setAttribute('role', 'status');
        element.prepend(spinner);
    },

    /**
     * Hide loading state on element
     * @param {HTMLElement} element - Element to hide loading state
     */
    hideLoading(element) {
        element.classList.remove('loading');
        const spinner = element.querySelector('.spinner-border');
        if (spinner) {
            spinner.remove();
        }
    },

    /**
     * Show success message
     * @param {string} message - Success message
     * @param {HTMLElement} container - Container to show message in
     */
    showSuccess(message, container = document.body) {
        this.showAlert(message, 'success', container);
    },

    /**
     * Show error message
     * @param {string} message - Error message
     * @param {HTMLElement} container - Container to show message in
     */
    showError(message, container = document.body) {
        this.showAlert(message, 'danger', container);
    },

    /**
     * Show alert message
     * @param {string} message - Alert message
     * @param {string} type - Alert type (success, danger, warning, info)
     * @param {HTMLElement} container - Container to show alert in
     */
    showAlert(message, type, container) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        container.insertBefore(alert, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    },

    /**
     * Format date for display
     * @param {string|Date} date - Date to format
     * @returns {string} - Formatted date
     */
    formatDate(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    /**
     * Format time for display
     * @param {string} time - Time to format (HH:MM format)
     * @returns {string} - Formatted time
     */
    formatTime(time) {
        if (!time) return '';
        const [hours, minutes] = time.split(':');
        const date = new Date();
        date.setHours(parseInt(hours), parseInt(minutes));
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    },

    /**
     * Format date range for display
     * @param {string|Date} startDate - Start date
     * @param {string|Date} endDate - End date
     * @returns {string} - Formatted date range
     */
    formatDateRange(startDate, endDate) {
        if (!startDate && !endDate) return '';
        if (!endDate) return this.formatDate(startDate);
        if (!startDate) return this.formatDate(endDate);

        const start = new Date(startDate);
        const end = new Date(endDate);
        
        const startFormatted = start.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric'
        });
        
        const endFormatted = end.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });

        return `${startFormatted} - ${endFormatted}`;
    },

    /**
     * Validate form data
     * @param {HTMLFormElement} form - Form to validate
     * @returns {Object} - Validation result with isValid and errors
     */
    validateForm(form) {
        const errors = {};
        let isValid = true;

        // Clear previous validation states
        form.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(el => {
            el.remove();
        });

        // Check required fields
        form.querySelectorAll('[required]').forEach(field => {
            if (!field.value.trim()) {
                errors[field.name] = 'This field is required';
                isValid = false;
                this.showFieldError(field, errors[field.name]);
            }
        });

        // Check date fields
        form.querySelectorAll('input[type="date"]').forEach(field => {
            if (field.value && !this.isValidDate(field.value)) {
                errors[field.name] = 'Please enter a valid date';
                isValid = false;
                this.showFieldError(field, errors[field.name]);
            }
        });

        // Check time fields
        form.querySelectorAll('input[type="time"]').forEach(field => {
            if (field.value && !this.isValidTime(field.value)) {
                errors[field.name] = 'Please enter a valid time';
                isValid = false;
                this.showFieldError(field, errors[field.name]);
            }
        });

        return { isValid, errors };
    },

    /**
     * Show field validation error
     * @param {HTMLElement} field - Form field element
     * @param {string} message - Error message
     */
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        field.parentNode.appendChild(feedback);
    },

    /**
     * Check if date is valid
     * @param {string} dateString - Date string to validate
     * @returns {boolean} - Whether date is valid
     */
    isValidDate(dateString) {
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    },

    /**
     * Check if time is valid
     * @param {string} timeString - Time string to validate (HH:MM)
     * @returns {boolean} - Whether time is valid
     */
    isValidTime(timeString) {
        const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
        return timeRegex.test(timeString);
    },

    /**
     * Initialize the application
     */
    init() {
        console.log('Travel Planner application initialized');
        
        // Set up global error handling
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showError('An unexpected error occurred. Please try again.');
        });

        // Add fade-in animation to main container
        const main = document.querySelector('main');
        if (main) {
            main.classList.add('fade-in');
        }
    }
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    TravelPlanner.init();
});

// Export for use in other scripts
window.TravelPlanner = TravelPlanner;