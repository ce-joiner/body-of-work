/**
 * Photo Selection Module
 * Handles photo selection and bulk actions functionality
 */

class PhotoSelection {
    constructor() {
        this.isInitialized = false;
        this.photoCards = [];
        this.selectAllBtn = null;
        this.selectNoneBtn = null;
        this.bulkActions = null;
        this.selectionStatus = null;
        this.bulkForm = null;
    }

    /**
     * Initialize photo selection functionality
     */
    init() {
        // Check if we're on a page with photo cards
        this.photoCards = document.querySelectorAll('.photo-card');
        if (this.photoCards.length === 0) {
            return; // No photos on this page
        }

        // Get DOM elements
        this.selectAllBtn = document.getElementById('select-all');
        this.selectNoneBtn = document.getElementById('select-none');
        this.bulkActions = document.getElementById('bulk-actions');
        this.selectionStatus = document.getElementById('selection-status');
        this.bulkForm = document.getElementById('bulk-form');

        if (!this.selectAllBtn || !this.selectNoneBtn) {
            return; // Required elements not found
        }

        // Set up event listeners
        this.setupPhotoCardListeners();
        this.setupControlButtons();
        this.setupBulkActions();

        this.isInitialized = true;
        console.log('Photo selection initialized');
    }

    /**
     * Set up event listeners for individual photo cards
     */
    setupPhotoCardListeners() {
        this.photoCards.forEach(card => {
            const checkbox = card.querySelector('.photo-select');
            if (!checkbox) return;

            // Click on card selects/deselects (but not during drag)
            card.addEventListener('click', (e) => {
                // Don't trigger on image clicks (those open detail)
                if (e.target.tagName === 'IMG') return;
                // Don't trigger on button clicks
                if (e.target.closest('.photo-actions')) return;
                // Don't trigger on drag handle
                if (e.target.closest('.drag-handle')) return;
                // Don't trigger if currently dragging
                if (document.body.classList.contains('photo-dragging')) return;

                checkbox.checked = !checkbox.checked;
                this.updateSelection();
            });

            // Checkbox change event
            checkbox.addEventListener('change', () => this.updateSelection());
        });
    }

    /**
     * Set up control buttons (Select All, Select None)
     */
    setupControlButtons() {
        this.selectAllBtn.addEventListener('click', () => {
            this.photoCards.forEach(card => {
                const checkbox = card.querySelector('.photo-select');
                if (checkbox) checkbox.checked = true;
            });
            this.updateSelection();
        });

        this.selectNoneBtn.addEventListener('click', () => {
            this.photoCards.forEach(card => {
                const checkbox = card.querySelector('.photo-select');
                if (checkbox) checkbox.checked = false;
            });
            this.updateSelection();
        });
    }

    /**
     * Set up bulk actions form
     */
    setupBulkActions() {
        if (!this.bulkForm) return;

        const bulkActionSelect = document.getElementById('bulk-action-select');
        if (!bulkActionSelect) return;

        this.bulkForm.addEventListener('submit', (e) => {
            const action = bulkActionSelect.value;
            const selectedCount = document.querySelectorAll('.photo-select:checked').length;

            if (!action) {
                e.preventDefault();
                alert('Please select an action first.');
                return;
            }

            if (selectedCount === 0) {
                e.preventDefault();
                alert('Please select photos first.');
                return;
            }

            // Confirm destructive actions
            if (action === 'delete') {
                const confirmMsg = `Are you sure you want to permanently delete ${selectedCount} photo${selectedCount !== 1 ? 's' : ''}? This action cannot be undone.`;
                if (!confirm(confirmMsg)) {
                    e.preventDefault();
                    return;
                }
            }

            // Show loading state
            const submitBtn = document.getElementById('bulk-submit');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '⏳ Processing...';
            }
        });
    }

    /**
     * Update selection state and UI
     */
    updateSelection() {
        const selected = document.querySelectorAll('.photo-select:checked');
        const selectedCount = selected.length;

        // Update visual selection
        this.photoCards.forEach(card => {
            const checkbox = card.querySelector('.photo-select');
            if (checkbox) {
                if (checkbox.checked) {
                    card.classList.add('selected');
                } else {
                    card.classList.remove('selected');
                }
            }
        });

        // Update selection status
        if (this.selectionStatus) {
            if (selectedCount === 0) {
                this.selectionStatus.textContent = 'Click photos to select them';
                if (this.bulkActions) this.bulkActions.style.display = 'none';
            } else {
                this.selectionStatus.textContent = `${selectedCount} photo${selectedCount !== 1 ? 's' : ''} selected`;
                if (this.bulkActions) this.bulkActions.style.display = 'block';
            }
        }

        // Update bulk form
        const selectedCountSpan = document.getElementById('selected-count');
        if (selectedCountSpan) {
            selectedCountSpan.textContent = selectedCount;
        }

        // Update hidden input with selected IDs
        const bulkIdsInput = document.getElementById('bulk-photo-ids');
        if (bulkIdsInput) {
            const selectedIds = Array.from(selected).map(cb => cb.value);
            bulkIdsInput.value = selectedIds.join(',');
        }
    }

    /**
     * Refresh selection (useful after adding new photos)
     */
    refresh() {
        if (this.isInitialized) {
            this.photoCards = document.querySelectorAll('.photo-card');
            this.setupPhotoCardListeners();
        }
    }

    /**
     * Clear all selections
     */
    clearSelection() {
        this.photoCards.forEach(card => {
            const checkbox = card.querySelector('.photo-select');
            if (checkbox) checkbox.checked = false;
        });
        this.updateSelection();
    }

    /**
     * Get selected photo IDs
     */
    getSelectedIds() {
        const selected = document.querySelectorAll('.photo-select:checked');
        return Array.from(selected).map(cb => cb.value);
    }

    /**
     * Select specific photos by ID
     */
    selectPhotos(photoIds) {
        photoIds.forEach(id => {
            const checkbox = document.querySelector(`.photo-select[value="${id}"]`);
            if (checkbox) checkbox.checked = true;
        });
        this.updateSelection();
    }
}

// Global function for opening photo detail (called from onclick in template)
function openPhotoDetail(photoId) {
    // Don't open if currently dragging
    if (document.body.classList.contains('photo-dragging')) {
        return;
    }
    window.location.href = `/projects/photos/${photoId}/`;
}

// Create global instance
window.PhotoSelection = PhotoSelection;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (!window.photoSelectionInstance) {
        window.photoSelectionInstance = new PhotoSelection();
        window.photoSelectionInstance.init();
    }
});

// Export for module systems (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PhotoSelection;
}