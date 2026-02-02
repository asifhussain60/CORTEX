/**
 * CORTEX SPA - Data Binder Component
 * Binds JSON data to DOM elements with data-bind attributes
 * Version: 1.0.0
 */

class DataBinder {
    constructor(data = {}) {
        this.data = data;
        this.formatters = {
            number: (v) => this.formatNumber(v),
            percent: (v) => `${v}%`,
            date: (v) => this.formatDate(v),
            datetime: (v) => this.formatDateTime(v),
            bytes: (v) => this.formatBytes(v),
            duration: (v) => this.formatDuration(v),
            severity: (v) => v?.toLowerCase() || 'unknown'
        };
    }
    
    /**
     * Set the data source
     */
    setData(data) {
        this.data = data;
    }
    
    /**
     * Get a value from the data using dot notation path
     */
    getValue(path) {
        if (!path) return undefined;
        
        return path.split('.').reduce((obj, key) => {
            if (obj === null || obj === undefined) return undefined;
            
            // Handle array access like items[0]
            const match = key.match(/^(\w+)\[(\d+)\]$/);
            if (match) {
                const [, arrayKey, index] = match;
                return obj[arrayKey]?.[parseInt(index)];
            }
            
            return obj[key];
        }, this.data);
    }
    
    /**
     * Check if a data path exists and has a value
     */
    hasValue(path) {
        const value = this.getValue(path);
        if (value === null || value === undefined) return false;
        if (Array.isArray(value)) return value.length > 0;
        if (typeof value === 'object') return Object.keys(value).length > 0;
        return true;
    }
    
    /**
     * Bind data to all elements with data-bind attribute
     */
    bind(container = document) {
        // Bind text content
        container.querySelectorAll('[data-bind]').forEach(el => {
            const path = el.getAttribute('data-bind');
            const format = el.getAttribute('data-format');
            const fallback = el.getAttribute('data-fallback') || '-';
            
            let value = this.getValue(path);
            
            if (value === undefined || value === null) {
                el.textContent = fallback;
                return;
            }
            
            if (format && this.formatters[format]) {
                value = this.formatters[format](value);
            }
            
            el.textContent = value;
        });
        
        // Bind attributes
        container.querySelectorAll('[data-bind-attr]').forEach(el => {
            const bindings = el.getAttribute('data-bind-attr').split(';');
            bindings.forEach(binding => {
                const [attr, path] = binding.split(':').map(s => s.trim());
                const value = this.getValue(path);
                if (value !== undefined && value !== null) {
                    el.setAttribute(attr, value);
                }
            });
        });
        
        // Bind CSS classes based on conditions
        container.querySelectorAll('[data-bind-class]').forEach(el => {
            const config = el.getAttribute('data-bind-class');
            try {
                const bindings = JSON.parse(config);
                Object.entries(bindings).forEach(([className, condition]) => {
                    const value = this.getValue(condition.path);
                    const matches = this.evaluateCondition(value, condition);
                    el.classList.toggle(className, matches);
                });
            } catch (e) {
                console.warn('DataBinder: Invalid data-bind-class config', config);
            }
        });
        
        // Conditional visibility
        container.querySelectorAll('[data-show-if]').forEach(el => {
            const path = el.getAttribute('data-show-if');
            const hasData = this.hasValue(path);
            el.style.display = hasData ? '' : 'none';
        });
        
        container.querySelectorAll('[data-hide-if]').forEach(el => {
            const path = el.getAttribute('data-hide-if');
            const hasData = this.hasValue(path);
            el.style.display = hasData ? 'none' : '';
        });
        
        // Conditional existence (removes from DOM)
        container.querySelectorAll('[data-if]').forEach(el => {
            const path = el.getAttribute('data-if');
            if (!this.hasValue(path)) {
                el.remove();
            }
        });
    }
    
    /**
     * Render a list/array of items using a template
     */
    renderList(containerId, templateId, dataPath, options = {}) {
        const container = document.getElementById(containerId);
        const template = document.getElementById(templateId);
        
        if (!container || !template) {
            console.warn(`DataBinder: Container or template not found: ${containerId}, ${templateId}`);
            return;
        }
        
        const items = this.getValue(dataPath);
        if (!Array.isArray(items)) {
            container.innerHTML = options.emptyHtml || '<div class="no-data">No data available</div>';
            return;
        }
        
        const limit = options.limit || items.length;
        const fragment = document.createDocumentFragment();
        
        items.slice(0, limit).forEach((item, index) => {
            const clone = template.content.cloneNode(true);
            
            // Create a temporary binder for this item
            const itemBinder = new DataBinder(item);
            itemBinder.bind(clone);
            
            // Add index to elements that need it
            clone.querySelectorAll('[data-index]').forEach(el => {
                el.textContent = index + 1;
            });
            
            fragment.appendChild(clone);
        });
        
        container.innerHTML = '';
        container.appendChild(fragment);
        
        // Show "more" indicator if truncated
        if (items.length > limit && options.showMore) {
            const moreEl = document.createElement('div');
            moreEl.className = 'text-center text-muted py-4';
            moreEl.textContent = `+ ${items.length - limit} more items`;
            container.appendChild(moreEl);
        }
    }
    
    evaluateCondition(value, condition) {
        if (condition.equals !== undefined) return value === condition.equals;
        if (condition.notEquals !== undefined) return value !== condition.notEquals;
        if (condition.gt !== undefined) return value > condition.gt;
        if (condition.gte !== undefined) return value >= condition.gte;
        if (condition.lt !== undefined) return value < condition.lt;
        if (condition.lte !== undefined) return value <= condition.lte;
        if (condition.contains !== undefined) return String(value).includes(condition.contains);
        if (condition.matches !== undefined) return new RegExp(condition.matches).test(value);
        return Boolean(value);
    }
    
    // Formatters
    formatNumber(value) {
        if (typeof value !== 'number') return value;
        if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M';
        if (value >= 1000) return (value / 1000).toFixed(1) + 'K';
        return value.toLocaleString();
    }
    
    formatDate(value) {
        if (!value) return '-';
        const date = new Date(value);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }
    
    formatDateTime(value) {
        if (!value) return '-';
        const date = new Date(value);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    formatDuration(ms) {
        if (ms < 1000) return ms + 'ms';
        if (ms < 60000) return (ms / 1000).toFixed(1) + 's';
        if (ms < 3600000) return (ms / 60000).toFixed(1) + 'm';
        return (ms / 3600000).toFixed(1) + 'h';
    }
    
    /**
     * Add a custom formatter
     */
    addFormatter(name, fn) {
        this.formatters[name] = fn;
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataBinder;
}
