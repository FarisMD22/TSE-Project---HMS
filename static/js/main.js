// static/js/main.js

// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('#flash-messages .alert');

    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(function() {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 300);
        }, 5000);
    });
});

// Add slideOut animation to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Utility Functions
const Utils = {
    // Format currency
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('ms-MY', {
            style: 'currency',
            currency: 'MYR'
        }).format(amount);
    },

    // Format date
    formatDate: function(dateString) {
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        return new Date(dateString).toLocaleDateString('ms-MY', options);
    },

    // Show loading spinner
    showLoading: function(element) {
        const originalContent = element.innerHTML;
        element.innerHTML = '<span class="loading"></span> Loading...';
        element.disabled = true;

        return function() {
            element.innerHTML = originalContent;
            element.disabled = false;
        };
    },

    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Show confirmation dialog
    confirm: function(message, onConfirm, onCancel) {
        if (confirm(message)) {
            if (onConfirm) onConfirm();
        } else {
            if (onCancel) onCancel();
        }
    },

    // Show notification
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.innerHTML = `
            ${message}
            <button onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        let container = document.getElementById('flash-messages');
        if (!container) {
            container = document.createElement('div');
            container.id = 'flash-messages';
            document.body.appendChild(container);
        }

        container.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease-out forwards';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, 5000);
    }
};

// API Helper
const API = {
    // Base fetch function with error handling
    request: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            Utils.showNotification('An error occurred. Please try again.', 'error');
            throw error;
        }
    },

    // GET request
    get: function(url) {
        return this.request(url);
    },

    // POST request
    post: function(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // PUT request
    put: function(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // DELETE request
    delete: function(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }
};

// Form Validation
const Validator = {
    // Email validation
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Phone validation
    isValidPhone: function(phone) {
        const phoneRegex = /^[6-9]\d{9}$/;
        return phoneRegex.test(phone.replace(/\D/g, ''));
    },

    // Required field validation
    isRequired: function(value) {
        return value && value.trim().length > 0;
    },

    // Minimum length validation
    minLength: function(value, min) {
        return value && value.length >= min;
    },

    // Maximum length validation
    maxLength: function(value, max) {
        return !value || value.length <= max;
    },

    // Number validation
    isNumber: function(value) {
        return !isNaN(value) && isFinite(value);
    },

    // Positive number validation
    isPositiveNumber: function(value) {
        return this.isNumber(value) && parseFloat(value) > 0;
    },

    // Validate form
    validateForm: function(formElement, rules) {
        const errors = {};
        let isValid = true;

        for (const [fieldName, fieldRules] of Object.entries(rules)) {
            const field = formElement.querySelector(`[name="${fieldName}"]`);
            const value = field ? field.value.trim() : '';

            for (const rule of fieldRules) {
                if (!rule.validator(value)) {
                    errors[fieldName] = rule.message;
                    isValid = false;
                    break;
                }
            }
        }

        return { isValid, errors };
    },

    // Show field errors
    showFieldErrors: function(errors) {
        // Clear previous errors
        document.querySelectorAll('.field-error').forEach(el => el.remove());

        for (const [fieldName, message] of Object.entries(errors)) {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (field) {
                const errorElement = document.createElement('div');
                errorElement.className = 'field-error';
                errorElement.style.color = '#dc3545';
                errorElement.style.fontSize = '0.8rem';
                errorElement.style.marginTop = '0.25rem';
                errorElement.textContent = message;

                field.parentNode.appendChild(errorElement);
                field.style.borderColor = '#dc3545';
            }
        }
    },

    // Clear field errors
    clearFieldErrors: function() {
        document.querySelectorAll('.field-error').forEach(el => el.remove());
        document.querySelectorAll('.form-control').forEach(el => {
            el.style.borderColor = '';
        });
    }
};

// Data Table Enhancement
class DataTable {
    constructor(tableElement, options = {}) {
        this.table = tableElement;
        this.options = {
            searchable: true,
            sortable: true,
            pagination: false,
            ...options
        };

        this.init();
    }

    init() {
        if (this.options.searchable) {
            this.addSearch();
        }

        if (this.options.sortable) {
            this.addSorting();
        }
    }

    addSearch() {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search...';
        searchInput.className = 'form-control';
        searchInput.style.width = '300px';
        searchInput.style.marginBottom = '1rem';

        this.table.parentNode.insertBefore(searchInput, this.table);

        searchInput.addEventListener('input', Utils.debounce((e) => {
            this.search(e.target.value);
        }, 300));
    }

    search(query) {
        const rows = this.table.querySelectorAll('tbody tr');
        const searchTerm = query.toLowerCase();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }

    addSorting() {
        const headers = this.table.querySelectorAll('thead th');

        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.style.userSelect = 'none';
            header.addEventListener('click', () => this.sort(index));

            // Add sort indicator
            const sortIcon = document.createElement('i');
            sortIcon.className = 'fas fa-sort';
            sortIcon.style.marginLeft = '0.5rem';
            sortIcon.style.opacity = '0.5';
            header.appendChild(sortIcon);
        });
    }

    sort(columnIndex) {
        const tbody = this.table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const header = this.table.querySelectorAll('thead th')[columnIndex];
        const sortIcon = header.querySelector('i');

        // Determine sort direction
        const isAscending = !header.classList.contains('sort-desc');

        // Clear all sort classes
        this.table.querySelectorAll('thead th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
            const icon = th.querySelector('i');
            if (icon) icon.className = 'fas fa-sort';
        });

        // Set sort class and icon
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        sortIcon.className = isAscending ? 'fas fa-sort-up' : 'fas fa-sort-down';

        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();

            // Try to parse as numbers
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);

            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? aNum - bNum : bNum - aNum;
            }

            // String comparison
            return isAscending
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        });

        // Reorder DOM
        rows.forEach(row => tbody.appendChild(row));
    }
}

// Modal Management
class Modal {
    constructor(modalElement) {
        this.modal = modalElement;
        this.init();
    }

    init() {
        // Close on background click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });

        // Close button
        const closeBtn = this.modal.querySelector('.close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }
    }

    open() {
        this.modal.style.display = 'block';
        document.body.style.overflow = 'hidden';

        // Focus first input
        const firstInput = this.modal.querySelector('input, select, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    close() {
        this.modal.style.display = 'none';
        document.body.style.overflow = '';
    }

    isOpen() {
        return this.modal.style.display === 'block';
    }
}

// Chart Helper Functions
const ChartHelpers = {
    // Default chart options
    getDefaultOptions: function() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            }
        };
    },

    // Color palette
    colors: [
        '#667eea',
        '#764ba2',
        '#28a745',
        '#dc3545',
        '#ffc107',
        '#17a2b8',
        '#6f42c1',
        '#fd7e14',
        '#20c997',
        '#e83e8c'
    ],

    // Generate colors
    generateColors: function(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(this.colors[i % this.colors.length]);
        }
        return colors;
    }
};

// Initialize data tables when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all data tables
    document.querySelectorAll('.data-table table').forEach(table => {
        new DataTable(table);
    });

    // Initialize all modals
    document.querySelectorAll('.modal').forEach(modalElement => {
        new Modal(modalElement);
    });

    // Add loading states to buttons
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const hideLoading = Utils.showLoading(submitBtn);

                // Reset loading state after 5 seconds (fallback)
                setTimeout(hideLoading, 5000);
            }
        });
    });

    // Enhanced form validation
    document.querySelectorAll('input, select, textarea').forEach(field => {
        field.addEventListener('blur', function() {
            // Clear error styling when user starts typing
            this.style.borderColor = '';
            const errorElement = this.parentNode.querySelector('.field-error');
            if (errorElement) {
                errorElement.remove();
            }
        });
    });
});

// Export utilities for global use
window.Utils = Utils;
window.API = API;
window.Validator = Validator;
window.DataTable = DataTable;
window.Modal = Modal;
window.ChartHelpers = ChartHelpers;