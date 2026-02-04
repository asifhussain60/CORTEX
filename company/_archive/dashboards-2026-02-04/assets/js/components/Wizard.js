/**
 * CORTEX SPA - Wizard Component
 * Multi-step wizard navigation for Architecture tab
 * Version: 1.0.0
 */

class Wizard {
    /**
     * Initialize wizard
     * @param {string} containerSelector - CSS selector for wizard container
     * @param {Object} options - Configuration options
     */
    constructor(containerSelector, options = {}) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            throw new Error(`Wizard container not found: ${containerSelector}`);
        }
        
        this.options = {
            onStepChange: options.onStepChange || (() => {}),
            onComplete: options.onComplete || (() => {}),
            allowSkip: options.allowSkip !== false,
            ...options
        };
        
        this.currentStep = 0;
        this.steps = [];
        this.initialized = false;
        
        this._initialize();
    }
    
    /**
     * Initialize wizard DOM structure
     * @private
     */
    _initialize() {
        // Find all wizard steps
        this.stepElements = Array.from(this.container.querySelectorAll('.wizard__step'));
        this.steps = this.stepElements.map((el, i) => ({
            id: i,
            element: el,
            title: el.dataset.stepTitle || `Step ${i + 1}`,
            visited: false,
            valid: true
        }));
        
        if (this.steps.length === 0) {
            console.warn('No wizard steps found');
            return;
        }
        
        // Create breadcrumb navigation
        this._createBreadcrumb();
        
        // Create navigation buttons
        this._createNavigation();
        
        // Show first step
        this.goToStep(0);
        
        this.initialized = true;
    }
    
    /**
     * Create breadcrumb navigation
     * @private
     */
    _createBreadcrumb() {
        let breadcrumb = this.container.querySelector('.wizard__breadcrumb');
        
        if (!breadcrumb) {
            breadcrumb = document.createElement('div');
            breadcrumb.className = 'wizard__breadcrumb';
            this.container.insertBefore(breadcrumb, this.container.firstChild);
        }
        
        breadcrumb.innerHTML = this.steps.map((step, i) => `
            <div class="wizard__breadcrumb-item ${i === 0 ? 'active' : ''}" data-step="${i}">
                <span class="wizard__breadcrumb-number">${i + 1}</span>
                <span class="wizard__breadcrumb-label">${step.title}</span>
            </div>
        `).join('');
        
        // Add click handlers
        breadcrumb.querySelectorAll('.wizard__breadcrumb-item').forEach((item, i) => {
            item.addEventListener('click', () => {
                if (this.options.allowSkip || this.steps[i].visited) {
                    this.goToStep(i);
                }
            });
        });
    }
    
    /**
     * Create navigation buttons
     * @private
     */
    _createNavigation() {
        let nav = this.container.querySelector('.wizard__navigation');
        
        if (!nav) {
            nav = document.createElement('div');
            nav.className = 'wizard__navigation';
            this.container.appendChild(nav);
        }
        
        nav.innerHTML = `
            <button class="wizard__btn wizard__btn--prev" data-action="prev">
                <span class="wizard__btn-icon">←</span>
                Previous
            </button>
            <button class="wizard__btn wizard__btn--next" data-action="next">
                Next
                <span class="wizard__btn-icon">→</span>
            </button>
            <button class="wizard__btn wizard__btn--complete" data-action="complete" style="display: none;">
                Complete
                <span class="wizard__btn-icon">✓</span>
            </button>
        `;
        
        // Add click handlers
        nav.querySelector('[data-action="prev"]').addEventListener('click', () => this.previous());
        nav.querySelector('[data-action="next"]').addEventListener('click', () => this.next());
        nav.querySelector('[data-action="complete"]').addEventListener('click', () => this.complete());
    }
    
    /**
     * Go to specific step
     * @param {number} stepIndex - Step index to navigate to
     */
    goToStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.steps.length) {
            console.warn(`Invalid step index: ${stepIndex}`);
            return;
        }
        
        // Mark current step as visited
        if (this.steps[this.currentStep]) {
            this.steps[this.currentStep].visited = true;
        }
        
        // Hide all steps
        this.stepElements.forEach(el => el.classList.remove('active'));
        
        // Show target step
        this.stepElements[stepIndex].classList.add('active');
        
        // Update breadcrumb
        const breadcrumbItems = this.container.querySelectorAll('.wizard__breadcrumb-item');
        breadcrumbItems.forEach((item, i) => {
            item.classList.toggle('active', i === stepIndex);
            item.classList.toggle('completed', this.steps[i].visited && i !== stepIndex);
        });
        
        // Update navigation buttons
        this._updateNavigation(stepIndex);
        
        // Update current step
        const previousStep = this.currentStep;
        this.currentStep = stepIndex;
        
        // Trigger callback
        this.options.onStepChange({
            currentStep: stepIndex,
            previousStep: previousStep,
            step: this.steps[stepIndex]
        });
    }
    
    /**
     * Update navigation button visibility
     * @private
     */
    _updateNavigation(stepIndex) {
        const prevBtn = this.container.querySelector('[data-action="prev"]');
        const nextBtn = this.container.querySelector('[data-action="next"]');
        const completeBtn = this.container.querySelector('[data-action="complete"]');
        
        if (prevBtn) prevBtn.style.display = stepIndex === 0 ? 'none' : 'inline-flex';
        
        const isLastStep = stepIndex === this.steps.length - 1;
        if (nextBtn) nextBtn.style.display = isLastStep ? 'none' : 'inline-flex';
        if (completeBtn) completeBtn.style.display = isLastStep ? 'inline-flex' : 'none';
    }
    
    /**
     * Navigate to next step
     */
    next() {
        if (this.currentStep < this.steps.length - 1) {
            this.goToStep(this.currentStep + 1);
        }
    }
    
    /**
     * Navigate to previous step
     */
    previous() {
        if (this.currentStep > 0) {
            this.goToStep(this.currentStep - 1);
        }
    }
    
    /**
     * Complete wizard
     */
    complete() {
        this.steps.forEach(step => step.visited = true);
        this.options.onComplete({
            steps: this.steps,
            currentStep: this.currentStep
        });
    }
    
    /**
     * Reset wizard to first step
     */
    reset() {
        this.steps.forEach(step => step.visited = false);
        this.goToStep(0);
    }
    
    /**
     * Validate current step
     * @param {boolean} valid - Whether step is valid
     */
    validateStep(valid) {
        this.steps[this.currentStep].valid = valid;
        const nextBtn = this.container.querySelector('[data-action="next"]');
        const completeBtn = this.container.querySelector('[data-action="complete"]');
        
        if (nextBtn) nextBtn.disabled = !valid;
        if (completeBtn) completeBtn.disabled = !valid;
    }
    
    /**
     * Get current step index
     * @returns {number}
     */
    getCurrentStep() {
        return this.currentStep;
    }
    
    /**
     * Get total number of steps
     * @returns {number}
     */
    getTotalSteps() {
        return this.steps.length;
    }
    
    /**
     * Destroy wizard instance
     */
    destroy() {
        const breadcrumb = this.container.querySelector('.wizard__breadcrumb');
        const nav = this.container.querySelector('.wizard__navigation');
        
        if (breadcrumb) breadcrumb.remove();
        if (nav) nav.remove();
        
        this.stepElements.forEach(el => el.classList.remove('active'));
        this.initialized = false;
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Wizard;
}
