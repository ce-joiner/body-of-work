// Body of Work - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the app
    initializeApp();
});

function initializeApp() {
    // Auto-hide messages after 5 seconds
    initializeMessages();
    
    // Initialize form enhancements
    initializeForms();
    
    // Initialize navigation enhancements
    initializeNavigation();
    
    console.log('Body of Work app initialized');
}

// Message handling
function initializeMessages() {
    const messages = document.querySelectorAll('.alert');
    
    messages.forEach(function(message) {
        // Auto-hide after 5 seconds
        setTimeout(function() {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-20px)';
            
            // Remove from DOM after animation
            setTimeout(function() {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 300);
        }, 5000);
        
        // Add click to dismiss functionality
        message.style.cursor = 'pointer';
        message.addEventListener('click', function() {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-20px)';
            
            setTimeout(function() {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 300);
        });
    });
}

// Form enhancements
function initializeForms() {
    // File input preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            handleFilePreview(this);
        });
    });
    
    // Form validation styling
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            addLoadingState(form);
        });
    });
}

// File upload preview functionality
function handleFilePreview(input) {
    const file = input.files[0];
    if (!file) return;
    
    // Update the label text if it exists
    const label = input.parentNode.querySelector('.file-input-label');
    if (label) {
        label.innerHTML = `
            <span class="file-input-icon">✅</span>
            <strong>Selected:</strong> ${file.name}
            <br><small>Click to change</small>
        `;
        label.style.borderColor = '#28a745';
        label.style.backgroundColor = '#d4edda';
        label.style.color = '#155724';
    }
    
    // If it's an image, show a preview (for later use with photo uploads)
    if (file.type.startsWith('image/')) {
        createImagePreview(file, input);
    }
}

// Create image preview (useful for photo uploads later)
function createImagePreview(file, input) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        // Remove existing preview
        const existingPreview = input.parentNode.querySelector('.image-preview');
        if (existingPreview) {
            existingPreview.remove();
        }
        
        // Create container for the image preview
        const preview = document.createElement('div');
        preview.className = 'image-preview';
        preview.style.cssText = `
            margin-top: 1rem;
            text-align: center;
            padding: 1rem;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            background-color: #f8f9fa;
        `;
        // Create the actual image element
        const img = document.createElement('img');
        // e.target.result contains the file data as a data URL
        img.src = e.target.result;
        img.style.cssText = `
            max-width: 200px;
            max-height: 200px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        `;
        
        preview.appendChild(img);
        // Add the preview container next to the file input
        // input.parentNode gets the parent element
        input.parentNode.appendChild(preview);
    };

    // Start reading the file and convert it to a data URL (to be displayed in an <img> tag)
    // This triggers the reader.onload function above when complete
    reader.readAsDataURL(file);
}

// Add loading state to forms and prevent double submission
function addLoadingState(form) {
    const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
    if (submitButton) {
         // Store the original button text to restore later
        const originalText = submitButton.textContent || submitButton.value;
        submitButton.disabled = true;
        
        if (submitButton.tagName === 'BUTTON') {
            // For <button> elements, change innerHTML
            submitButton.innerHTML = '⏳ Processing...';
        } else {
            // For <input> elements, change value attribute
            submitButton.value = 'Processing...';
        }
        
        // Reset after 10 seconds (safety net)
        setTimeout(function() {
            submitButton.disabled = false;
            if (submitButton.tagName === 'BUTTON') {
                submitButton.innerHTML = originalText;
            } else {
                submitButton.value = originalText;
            }
        }, 10000);
    }
}

// Navigation enhancements
function initializeNavigation() {
    // highlight the current page in navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Loop through each navigation link
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            // Highlight the active link with background color and rounded corners
            link.style.backgroundColor = 'rgba(255,255,255,0.2)';
            link.style.borderRadius = '6px';
        }
    });
    
    // Mobile menu toggle (add hamburger menu later)
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', toggleMobileMenu);
    }
}

// Mobile menu toggle function (for future use)
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        navMenu.classList.toggle('mobile-open');
    }
}

// Utility functions for later use
// Creates notifications that slide in from the right
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        min-width: 300px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        
        // Remove from DOM after animation
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// CSRF token helper for AJAX requests (will need this later)
function getCookie(name) {
    // Initialize return value as null (cookie not found)
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        // Split document.cookie string into individual cookies
        const cookies = document.cookie.split(';');
        // Loop through each cookie to find the one I want
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if this cookie starts with target name
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                // Extract the value part after the '=' sign and decode it
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break; // Found the cookie, stop searching
            }
        }
    }
    return cookieValue;
}

// Set up CSRF for AJAX requests
// Automatically adds CSRF token to all AJAX requests
function setupCSRF() {
    const csrftoken = getCookie('csrftoken');
    
    // Set up jQuery AJAX (might use it later)
    if (typeof $ !== 'undefined') {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }
    
    return csrftoken;
}