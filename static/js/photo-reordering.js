/**
 * Photo Reordering Module
 * Handles drag & drop functionality for reordering photos in projects
 */

class PhotoReordering {
    constructor() {
        this.sortableInstance = null;
        this.isInitialized = false;
        this.projectId = null;
        this.photoGrid = null;
        this.dragInstructions = null;
    }

    /**
     * Initialize the photo reordering functionality
     */
    init() {
        // Check if we're on a page with a photo grid
        this.photoGrid = document.getElementById('photo-grid');
        if (!this.photoGrid) {
            return; // No photo grid on this page
        }

        // Check if SortableJS is available
        if (typeof Sortable === 'undefined') {
            console.warn('SortableJS not loaded. Drag & drop reordering disabled.');
            this.showFallbackMessage();
            return;
        }

        // Get project ID
        this.projectId = this.getProjectId();
        if (!this.projectId) {
            console.error('Could not determine project ID for photo reordering');
            return;
        }

        // Initialize drag & drop
        this.setupDragHandles();
        this.initializeSortable();
        this.setupInstructions();
        
        this.isInitialized = true;
        console.log('Photo reordering initialized for project', this.projectId);
    }

    /**
     * Add drag handles to photo cards
     */
    setupDragHandles() {
        const photoCards = this.photoGrid.querySelectorAll('.photo-card');
        
        photoCards.forEach(card => {
            // Skip if drag handle already exists
            if (card.querySelector('.drag-handle')) {
                return;
            }
            
            // Create drag handle
            const dragHandle = document.createElement('div');
            dragHandle.className = 'drag-handle';
            dragHandle.innerHTML = '⋮⋮';
            dragHandle.title = 'Drag to reorder';
            dragHandle.setAttribute('aria-label', 'Drag to reorder photo');
            
            // Add handle to card
            card.appendChild(dragHandle);
        });
    }

    /**
     * Initialize SortableJS instance
     */
    initializeSortable() {
        this.sortableInstance = new Sortable(this.photoGrid, {
            handle: '.drag-handle',
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            disabled: false,
            
            onStart: (evt) => this.handleDragStart(evt),
            onEnd: (evt) => this.handleDragEnd(evt),
            onMove: (evt) => this.handleDragMove(evt)
        });

        // Store instance globally for debugging
        window.photoSortable = this.sortableInstance;
    }

    /**
     * Handle drag start event
     */
    handleDragStart(evt) {
        // Add dragging class to body for global styling
        document.body.classList.add('photo-dragging');
        
        // Disable selection controls during drag
        this.toggleSelectionControls(false);
        
        // Disable photo links during drag
        this.togglePhotoLinks(false);
    }

    /**
     * Handle drag end event
     */
    handleDragEnd(evt) {
        // Remove dragging class
        document.body.classList.remove('photo-dragging');
        
        // Re-enable selection controls
        this.toggleSelectionControls(true);
        
        // Re-enable photo links
        this.togglePhotoLinks(true);
        
        // Save order if changed
        if (evt.oldIndex !== evt.newIndex) {
            this.savePhotoOrder();
        } else {
            this.updateInstructions('Drag photos to reorder them');
        }
    }

    /**
     * Handle drag move event (for additional validations if needed)
     */
    handleDragMove(evt) {
        // Can add custom logic here if needed
        return true; // Allow the move
    }

    /**
     * Save the new photo order to the server
     */
    async savePhotoOrder() {
        // Get current order of photo IDs
        const photoCards = this.photoGrid.querySelectorAll('.photo-card');
        const photoIds = Array.from(photoCards)
            .map(card => card.getAttribute('data-photo-id'))
            .filter(id => id); // Filter out any null/undefined IDs
        
        if (photoIds.length === 0) {
            console.warn('No photo IDs found for reordering');
            this.updateInstructions(' No photos to reorder', 'error');
            return;
        }
        
        // Show loading state
        this.showLoadingIndicator(true);
        this.updateInstructions('Saving order...');
        
        try {
            const response = await fetch(`/projects/${this.projectId}/photos/reorder/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    photo_ids: photoIds
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateInstructions('Order saved!', 'success');
                this.showNotification('Photo order saved successfully', 'success');
                
                // Add success animation to photos
                this.animateSuccessfulReorder();
                
                // Reset instructions after delay
                setTimeout(() => {
                    this.updateInstructions('Drag photos to reorder them');
                }, 2000);
            } else {
                throw new Error(data.message || 'Failed to save order');
            }
            
        } catch (error) {
            console.error('Error saving photo order:', error);
            this.updateInstructions(' Save failed', 'error');
            this.showNotification('Failed to save photo order. Please try again.', 'error');
            
            // Reset instructions after delay
            setTimeout(() => {
                this.updateInstructions('Drag photos to reorder them');
            }, 3000);
            
        } finally {
            this.showLoadingIndicator(false);
        }
    }

    /**
     * Get project ID from various sources
     */
    getProjectId() {
        // Try data attribute first
        const projectData = document.querySelector('[data-project-id]');
        if (projectData) {
            return projectData.getAttribute('data-project-id');
        }
        
        // Try URL path
        const pathMatch = window.location.pathname.match(/\/projects\/(\d+)\//);
        if (pathMatch) {
            return pathMatch[1];
        }
        
        // Try project links
        const detailLink = document.querySelector('a[href*="/projects/"]');
        if (detailLink) {
            const linkMatch = detailLink.href.match(/\/projects\/(\d+)\//);
            if (linkMatch) {
                return linkMatch[1];
            }
        }
        
        return null;
    }

    /**
     * Setup and manage drag instructions
     */
    setupInstructions() {
        this.dragInstructions = document.getElementById('drag-hint');
        if (!this.dragInstructions) {
        }
    }

    /**
     * Update instruction text and styling
     */
    updateInstructions(text, type = 'default') {
        if (!this.dragInstructions) return;
        
        this.dragInstructions.textContent = text;
        
        // Remove existing type classes
        this.dragInstructions.classList.remove('success', 'error', 'loading');
        
        // Add new type class
        if (type !== 'default') {
            this.dragInstructions.classList.add(type);
        }
    }

    /**
     * Toggle selection controls during drag
     */
    toggleSelectionControls(enable) {
        const selectionControls = document.querySelector('.selection-controls');
        if (selectionControls) {
            if (enable) {
                selectionControls.style.opacity = '1';
                selectionControls.style.pointerEvents = 'auto';
            } else {
                selectionControls.style.opacity = '0.5';
                selectionControls.style.pointerEvents = 'none';
            }
        }
    }

    /**
     * Toggle photo links during drag
     */
    togglePhotoLinks(enable) {
        const photoImages = this.photoGrid.querySelectorAll('.photo-image img');
        photoImages.forEach(img => {
            img.style.pointerEvents = enable ? 'auto' : 'none';
        });
    }

    /**
     * Show/hide loading indicator
     */
    showLoadingIndicator(show) {
        let indicator = document.getElementById('reorder-loading');
        
        if (show && !indicator) {
            // Create loading indicator
            indicator = document.createElement('div');
            indicator.id = 'reorder-loading';
            indicator.className = 'reorder-loading-indicator';
            indicator.innerHTML = `
                <div class="loading-content">
                    <div class="spinner"></div>
                    <span>Saving photo order...</span>
                </div>
            `;
            
            // Add to body
            document.body.appendChild(indicator);
            
        } else if (!show && indicator) {
            // Remove loading indicator
            indicator.remove();
        }
    }

    /**
     * Add success animation to reordered photos
     */
    animateSuccessfulReorder() {
        const photoCards = this.photoGrid.querySelectorAll('.photo-card');
        photoCards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('reorder-success');
                setTimeout(() => {
                    card.classList.remove('reorder-success');
                }, 600);
            }, index * 50); // Stagger the animations
        });
    }

    /**
     * Show notification (uses global function if available)
     */
    showNotification(message, type = 'info') {
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, type);
        } else {
            // Fallback to simple alert
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    /**
 * Get CSRF token for AJAX requests
 */
getCSRFToken() {
    // Try multiple methods to get CSRF token
    let token = null;
    
    // From meta tag
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        token = metaToken.getAttribute('content');
    }
    
    // From cookie (Django's default)
    if (!token) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                token = value;
                break;
            }
        }
    }
    
    // From form input (if present)
    if (!token) {
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            token = csrfInput.value;
        }
    }
    return token;
}

    /**
     * Show fallback message when SortableJS is not available
     */
    showFallbackMessage() {
        const photoGrid = document.getElementById('photo-grid');
        if (photoGrid && photoGrid.children.length > 1) {
            const message = document.createElement('div');
            message.className = 'alert alert-info';
            message.style.margin = '1rem 0';
            message.textContent = 'Drag & drop reordering is not available. Please refresh the page if you want to reorder photos.';
            
            photoGrid.parentNode.insertBefore(message, photoGrid);
        }
    }

    /**
     * Destroy the sortable instance (for cleanup)
     */
    destroy() {
        if (this.sortableInstance) {
            this.sortableInstance.destroy();
            this.sortableInstance = null;
        }
        
        // Remove drag handles
        const dragHandles = document.querySelectorAll('.drag-handle');
        dragHandles.forEach(handle => handle.remove());
        
        // Clean up global reference
        if (window.photoSortable) {
            delete window.photoSortable;
        }
        
        this.isInitialized = false;
    }

    /**
     * Refresh the sortable instance (useful after adding new photos)
     */
    refresh() {
        if (this.isInitialized) {
            this.setupDragHandles(); // Add handles to new photos
            // SortableJS automatically detects new elements
        }
    }
}

// Create global instance
window.PhotoReordering = PhotoReordering;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (!window.photoReorderingInstance) {
        window.photoReorderingInstance = new PhotoReordering();
        window.photoReorderingInstance.init();
    }
});

// Export for module systems (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PhotoReordering;
}