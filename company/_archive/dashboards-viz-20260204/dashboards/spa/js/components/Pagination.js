/**
 * CORTEX SPA - Pagination Component
 * Pagination controls for tables and lists
 * Version: 1.0.0
 */

class Pagination {
    /**
     * Initialize pagination
     * @param {string} containerSelector - CSS selector for pagination container
     * @param {Object} options - Configuration options
     */
    constructor(containerSelector, options = {}) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            throw new Error(`Pagination container not found: ${containerSelector}`);
        }
        
        this.options = {
            totalItems: options.totalItems || 0,
            itemsPerPage: options.itemsPerPage || 10,
            currentPage: options.currentPage || 1,
            maxPages: options.maxPages || 7,
            onPageChange: options.onPageChange || (() => {}),
            showFirstLast: options.showFirstLast !== false,
            showPageSize: options.showPageSize !== false,
            pageSizeOptions: options.pageSizeOptions || [10, 25, 50, 100],
            ...options
        };
        
        this.currentPage = this.options.currentPage;
        this.itemsPerPage = this.options.itemsPerPage;
        this.totalPages = Math.ceil(this.options.totalItems / this.itemsPerPage);
        
        this._render();
    }
    
    /**
     * Render pagination UI
     * @private
     */
    _render() {
        this.container.innerHTML = `
            <div class="pagination">
                <div class="pagination__info">
                    ${this._renderInfo()}
                </div>
                <div class="pagination__controls">
                    ${this._renderControls()}
                </div>
                ${this.options.showPageSize ? `
                    <div class="pagination__size">
                        ${this._renderPageSize()}
                    </div>
                ` : ''}
            </div>
        `;
        
        this._attachEventListeners();
    }
    
    /**
     * Render pagination info
     * @private
     */
    _renderInfo() {
        const start = Math.min((this.currentPage - 1) * this.itemsPerPage + 1, this.options.totalItems);
        const end = Math.min(this.currentPage * this.itemsPerPage, this.options.totalItems);
        
        return `
            <span class="pagination__info-text">
                Showing ${start} - ${end} of ${this.options.totalItems}
            </span>
        `;
    }
    
    /**
     * Render pagination controls
     * @private
     */
    _renderControls() {
        const pages = this._getPageNumbers();
        
        return `
            ${this.options.showFirstLast ? `
                <button class="pagination__btn" data-page="1" ${this.currentPage === 1 ? 'disabled' : ''}>
                    <span class="pagination__btn-icon">⟨⟨</span>
                </button>
            ` : ''}
            
            <button class="pagination__btn" data-page="${this.currentPage - 1}" ${this.currentPage === 1 ? 'disabled' : ''}>
                <span class="pagination__btn-icon">⟨</span>
                Previous
            </button>
            
            <div class="pagination__pages">
                ${pages.map(page => {
                    if (page === '...') {
                        return '<span class="pagination__ellipsis">...</span>';
                    }
                    return `
                        <button class="pagination__btn pagination__btn--page ${page === this.currentPage ? 'active' : ''}" 
                                data-page="${page}">
                            ${page}
                        </button>
                    `;
                }).join('')}
            </div>
            
            <button class="pagination__btn" data-page="${this.currentPage + 1}" ${this.currentPage === this.totalPages ? 'disabled' : ''}>
                Next
                <span class="pagination__btn-icon">⟩</span>
            </button>
            
            ${this.options.showFirstLast ? `
                <button class="pagination__btn" data-page="${this.totalPages}" ${this.currentPage === this.totalPages ? 'disabled' : ''}>
                    <span class="pagination__btn-icon">⟩⟩</span>
                </button>
            ` : ''}
        `;
    }
    
    /**
     * Render page size selector
     * @private
     */
    _renderPageSize() {
        return `
            <label class="pagination__size-label">
                Show:
                <select class="pagination__size-select">
                    ${this.options.pageSizeOptions.map(size => `
                        <option value="${size}" ${size === this.itemsPerPage ? 'selected' : ''}>
                            ${size}
                        </option>
                    `).join('')}
                </select>
                per page
            </label>
        `;
    }
    
    /**
     * Get page numbers to display
     * @private
     * @returns {Array<number|string>}
     */
    _getPageNumbers() {
        const maxPages = this.options.maxPages;
        const current = this.currentPage;
        const total = this.totalPages;
        
        if (total <= maxPages) {
            return Array.from({ length: total }, (_, i) => i + 1);
        }
        
        const pages = [];
        const halfMax = Math.floor(maxPages / 2);
        
        let startPage = Math.max(1, current - halfMax);
        let endPage = Math.min(total, current + halfMax);
        
        // Adjust if at boundaries
        if (current <= halfMax) {
            endPage = maxPages;
        } else if (current >= total - halfMax) {
            startPage = total - maxPages + 1;
        }
        
        // Add first page
        if (startPage > 1) {
            pages.push(1);
            if (startPage > 2) pages.push('...');
        }
        
        // Add page range
        for (let i = startPage; i <= endPage; i++) {
            pages.push(i);
        }
        
        // Add last page
        if (endPage < total) {
            if (endPage < total - 1) pages.push('...');
            pages.push(total);
        }
        
        return pages;
    }
    
    /**
     * Attach event listeners
     * @private
     */
    _attachEventListeners() {
        // Page button clicks
        this.container.querySelectorAll('[data-page]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = parseInt(e.currentTarget.dataset.page, 10);
                if (!isNaN(page) && page >= 1 && page <= this.totalPages) {
                    this.goToPage(page);
                }
            });
        });
        
        // Page size change
        const sizeSelect = this.container.querySelector('.pagination__size-select');
        if (sizeSelect) {
            sizeSelect.addEventListener('change', (e) => {
                this.setPageSize(parseInt(e.target.value, 10));
            });
        }
    }
    
    /**
     * Go to specific page
     * @param {number} page - Page number to navigate to
     */
    goToPage(page) {
        if (page < 1 || page > this.totalPages || page === this.currentPage) {
            return;
        }
        
        const previousPage = this.currentPage;
        this.currentPage = page;
        
        this._render();
        
        this.options.onPageChange({
            currentPage: page,
            previousPage: previousPage,
            itemsPerPage: this.itemsPerPage,
            totalPages: this.totalPages,
            totalItems: this.options.totalItems,
            startIndex: (page - 1) * this.itemsPerPage,
            endIndex: Math.min(page * this.itemsPerPage - 1, this.options.totalItems - 1)
        });
    }
    
    /**
     * Set page size
     * @param {number} size - Items per page
     */
    setPageSize(size) {
        if (size === this.itemsPerPage || size < 1) {
            return;
        }
        
        this.itemsPerPage = size;
        this.totalPages = Math.ceil(this.options.totalItems / this.itemsPerPage);
        
        // Adjust current page if necessary
        if (this.currentPage > this.totalPages) {
            this.currentPage = this.totalPages;
        }
        
        this._render();
        
        this.options.onPageChange({
            currentPage: this.currentPage,
            previousPage: this.currentPage,
            itemsPerPage: this.itemsPerPage,
            totalPages: this.totalPages,
            totalItems: this.options.totalItems,
            startIndex: (this.currentPage - 1) * this.itemsPerPage,
            endIndex: Math.min(this.currentPage * this.itemsPerPage - 1, this.options.totalItems - 1)
        });
    }
    
    /**
     * Update total items count
     * @param {number} totalItems - New total items count
     */
    updateTotalItems(totalItems) {
        this.options.totalItems = totalItems;
        this.totalPages = Math.ceil(totalItems / this.itemsPerPage);
        
        // Adjust current page if necessary
        if (this.currentPage > this.totalPages && this.totalPages > 0) {
            this.currentPage = this.totalPages;
        }
        
        this._render();
    }
    
    /**
     * Get current page
     * @returns {number}
     */
    getCurrentPage() {
        return this.currentPage;
    }
    
    /**
     * Get total pages
     * @returns {number}
     */
    getTotalPages() {
        return this.totalPages;
    }
    
    /**
     * Get items per page
     * @returns {number}
     */
    getItemsPerPage() {
        return this.itemsPerPage;
    }
    
    /**
     * Destroy pagination instance
     */
    destroy() {
        this.container.innerHTML = '';
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Pagination;
}
