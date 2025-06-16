/**
 * Delete Confirmations Module
 * Handles confirmation dialogs for deleting photos and projects
 */

class DeleteConfirmations {
    constructor() {
        this.isInitialized = false;
    }

    /**
     * Initialize delete confirmation functionality
     */
    init() {
        this.setupProjectDeleteConfirmation();
        this.isInitialized = true;
        console.log('Delete confirmations initialized');
    }

    /**
     * Setup project delete confirmation with type-to-confirm
     */
    setupProjectDeleteConfirmation() {
        const confirmInput = document.getElementById('confirm-input');
        const deleteButton = document.getElementById('delete-button');
        const inputFeedback = document.getElementById('input-feedback');
        const deleteForm = document.getElementById('delete-form');

        // Only run if we're on project delete page
        if (!confirmInput || !deleteButton || !deleteForm) {
            return;
        }

        const projectTitle = deleteButton.dataset.projectTitle || '';

        // Real-time validation
        confirmInput.addEventListener('input', function() {
            const inputValue = this.value.trim();
            
            if (inputValue === projectTitle) {
                deleteButton.disabled = false;
                deleteButton.classList.add('enabled');
                if (inputFeedback) {
                    inputFeedback.textContent = '✓ Confirmed';
                    inputFeedback.className = 'form-text success';
                }
            } else if (inputValue.length > 0) {
                deleteButton.disabled = true;
                deleteButton.classList.remove('enabled');
                if (inputFeedback) {
                    inputFeedback.textContent = 'Project title must match exactly';
                    inputFeedback.className = 'form-text error';
                }
            } else {
                deleteButton.disabled = true;
                deleteButton.classList.remove('enabled');
                if (inputFeedback) {
                    inputFeedback.textContent = '';
                    inputFeedback.className = 'form-text';
                }
            }
        });

        // Final confirmation on submit
        deleteForm.addEventListener('submit', function(e) {
            if (confirmInput.value.trim() !== projectTitle) {
                e.preventDefault();
                alert('Please type the project title exactly to confirm deletion.');
                confirmInput.focus();
                return false;
            }

            const photoCount = deleteButton.dataset.photoCount || '0';
            const finalConfirm = confirm(
                `Are you absolutely sure you want to delete "${projectTitle}" and all ${photoCount} photos? This action cannot be undone.`
            );
            
            if (!finalConfirm) {
                e.preventDefault();
                return false;
            }

            // Show deletion in progress
            deleteButton.disabled = true;
            deleteButton.innerHTML = '⏳ Deleting Project...';
        });
    }
}

/**
 * Simple photo delete confirmation with detailed warning
 */
function confirmPhotoDelete(photoTitle) {
    const message = `Are you sure you want to permanently delete "${photoTitle}"?\n\nThis action will:\n• Remove the photo from your project\n• Delete the image file from cloud storage\n• Remove all metadata and EXIF data\n\nThis cannot be undone.`;
    
    return confirm(message);
}

/**
 * Confirm project deletion from edit page
 */
function confirmProjectDelete(projectTitle) {
    const message = `Are you sure you want to delete the project "${projectTitle}"?\n\nThis will permanently delete:\n• All photos in the project\n• All project data and settings\n• All image files from cloud storage\n\nThis action cannot be undone.`;
    
    return confirm(message);
}

// Create global instance
window.DeleteConfirmations = DeleteConfirmations;

// Global functions for template use
window.confirmPhotoDelete = confirmPhotoDelete;
window.confirmProjectDelete = confirmProjectDelete;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (!window.deleteConfirmationsInstance) {
        window.deleteConfirmationsInstance = new DeleteConfirmations();
        window.deleteConfirmationsInstance.init();
    }
});

// Export for module systems (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DeleteConfirmations;
}