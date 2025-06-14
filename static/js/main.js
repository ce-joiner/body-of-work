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

// File upload preview functionality (updated for multiple files with CSS classes)
function handleFilePreview(input) {
    const files = input.files;
    if (!files || files.length === 0) return;
    
    // Store files in a way we can modify
    input.selectedFiles = Array.from(files);
    
    // Update the label text if it exists
    const label = input.parentNode.querySelector('.file-input-label');
    if (label) {
        updateLabelText(label, input.selectedFiles.length);
    }
    
    // Show previews for all selected images
    createMultipleImagePreviews(input.selectedFiles, input);
}

// Update label text based on file count
function updateLabelText(label, fileCount) {
    if (fileCount === 0) {
        label.innerHTML = `
            <span class="file-input-icon">📸</span>
            <strong>Choose images</strong>
            <br><small>Click to select files</small>
        `;
        label.className = label.className.replace('selected', 'default');
    } else if (fileCount === 1) {
        label.innerHTML = `
            <span class="file-input-icon">✅</span>
            <strong>Selected:</strong> 1 image
            <br><small>Click to change</small>
        `;
        label.className = label.className.replace('default', 'selected');
    } else {
        label.innerHTML = `
            <span class="file-input-icon">✅</span>
            <strong>Selected:</strong> ${fileCount} images
            <br><small>Click to change</small>
        `;
        label.className = label.className.replace('default', 'selected');
    }
}

// Create multiple image previews for batch uploads
function createMultipleImagePreviews(files, input) {
    // Remove existing preview containers
    const existingPreview = input.parentNode.querySelector('.image-preview-container');
    if (existingPreview) {
        existingPreview.remove();
    }
    
    const oldPreview = input.parentNode.querySelector('.image-preview');
    if (oldPreview) {
        oldPreview.remove();
    }
    
    // Don't show container if no files
    if (files.length === 0) return;
    
    // Create main container for all previews
    const previewContainer = document.createElement('div');
    previewContainer.className = 'image-preview-container';
    
    // Create grid for multiple images
    const previewGrid = document.createElement('div');
    previewGrid.className = 'preview-grid';
    
    // Process each image file
    files.forEach((file, index) => {
        if (file.type.startsWith('image/')) {
            createSingleImagePreview(file, previewGrid, index, input);
        }
    });
    
    previewContainer.appendChild(previewGrid);
    input.parentNode.appendChild(previewContainer);
}

// Create preview for a single image with remove button
function createSingleImagePreview(file, container, index, input) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const previewItem = document.createElement('div');
        previewItem.className = 'preview-item';
        
        // Create remove button
        const removeBtn = document.createElement('button');
        removeBtn.textContent = '×';
        removeBtn.type = 'button';
        removeBtn.className = 'remove-btn';
        
        // Remove button click handler
        removeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            removeFileFromSelection(input, index);
        });
        
        const img = document.createElement('img');
        img.src = e.target.result;
        img.alt = file.name;
        
        const filename = document.createElement('div');
        filename.className = 'preview-filename';
        filename.textContent = file.name.length > 20 ? 
            file.name.substring(0, 17) + '...' : file.name;
        
        previewItem.appendChild(removeBtn);
        previewItem.appendChild(img);
        previewItem.appendChild(filename);
        container.appendChild(previewItem);
    };
    
    reader.readAsDataURL(file);
}

// Remove a file from the selection
function removeFileFromSelection(input, indexToRemove) {
    // Remove the file from our custom array
    input.selectedFiles.splice(indexToRemove, 1);
    
    // Update the actual file input (create new FileList)
    const dt = new DataTransfer();
    input.selectedFiles.forEach(file => {
        dt.items.add(file);
    });
    input.files = dt.files;
    
    // Update the label
    const label = input.parentNode.querySelector('.file-input-label');
    if (label) {
        updateLabelText(label, input.selectedFiles.length);
    }
    
    // Recreate previews
    createMultipleImagePreviews(input.selectedFiles, input);
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