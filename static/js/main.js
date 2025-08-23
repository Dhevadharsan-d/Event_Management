// Main JavaScript file for Event Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            // Show loading state on submit buttons
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML || submitBtn.value;
                submitBtn.disabled = true;
                
                if (submitBtn.tagName === 'BUTTON') {
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
                } else {
                    submitBtn.value = 'Processing...';
                }

                // Re-enable after 10 seconds in case something goes wrong
                setTimeout(function() {
                    submitBtn.disabled = false;
                    if (submitBtn.tagName === 'BUTTON') {
                        submitBtn.innerHTML = originalText;
                    } else {
                        submitBtn.value = originalText;
                    }
                }, 10000);
            }
        });
    });

    // Search form auto-submit on filter change
    const searchForm = document.querySelector('form[action*="index"]');
    if (searchForm) {
        const statusSelect = searchForm.querySelector('#status');
        if (statusSelect) {
            statusSelect.addEventListener('change', function() {
                searchForm.submit();
            });
        }
    }

    // Date and time validation for event forms
    const eventForm = document.querySelector('form[action*="create_event"], form[action*="edit_event"]');
    if (eventForm) {
        const dateInput = eventForm.querySelector('#date');
        const timeInput = eventForm.querySelector('#time');
        
        if (dateInput) {
            // Set minimum date to today
            const today = new Date().toISOString().split('T')[0];
            dateInput.setAttribute('min', today);
            
            // Validate date on change
            dateInput.addEventListener('change', function() {
                const selectedDate = new Date(this.value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                if (selectedDate < today) {
                    this.setCustomValidity('Event date cannot be in the past');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
        
        // Validate time if date is today
        if (dateInput && timeInput) {
            function validateTime() {
                const selectedDate = new Date(dateInput.value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                if (selectedDate.getTime() === today.getTime() && timeInput.value) {
                    const selectedTime = timeInput.value;
                    const now = new Date();
                    const currentTime = now.getHours().toString().padStart(2, '0') + ':' + 
                                       now.getMinutes().toString().padStart(2, '0');
                    
                    if (selectedTime <= currentTime) {
                        timeInput.setCustomValidity('Event time must be in the future');
                    } else {
                        timeInput.setCustomValidity('');
                    }
                } else {
                    timeInput.setCustomValidity('');
                }
            }
            
            dateInput.addEventListener('change', validateTime);
            timeInput.addEventListener('change', validateTime);
        }
    }

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('button[data-bs-target="#deleteModal"], form[onsubmit*="confirm"]');
    deleteButtons.forEach(function(button) {
        if (button.tagName === 'FORM') {
            button.addEventListener('submit', function(event) {
                if (!confirm(button.getAttribute('onsubmit').match(/confirm\('([^']+)'\)/)[1])) {
                    event.preventDefault();
                }
            });
        }
    });

    // Progress bar animations
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        const width = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(function() {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = width;
        }, 100);
    });

    // Search input enhancements
    const searchInput = document.querySelector('#search');
    if (searchInput) {
        // Clear search button
        const clearButton = document.createElement('button');
        clearButton.type = 'button';
        clearButton.className = 'btn btn-outline-secondary';
        clearButton.innerHTML = '<i data-feather="x"></i>';
        clearButton.style.display = searchInput.value ? 'inline-block' : 'none';
        
        clearButton.addEventListener('click', function() {
            searchInput.value = '';
            searchInput.form.submit();
        });
        
        searchInput.addEventListener('input', function() {
            clearButton.style.display = this.value ? 'inline-block' : 'none';
        });
        
        // Add clear button after search input
        searchInput.parentNode.appendChild(clearButton);
        
        // Re-initialize feather icons for the new button
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }

    // Responsive table handling
    const tables = document.querySelectorAll('table');
    tables.forEach(function(table) {
        if (!table.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
});

// Utility function to format dates consistently
function formatDate(date, includeTime = false) {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    };
    
    if (includeTime) {
        options.hour = 'numeric';
        options.minute = '2-digit';
        options.hour12 = true;
    }
    
    return new Date(date).toLocaleDateString('en-US', options);
}

// Utility function to show toast messages
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}
