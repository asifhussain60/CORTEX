/**
 * HTML Utility Functions
 * Common HTML manipulation and security utilities
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

/**
 * Escape HTML to prevent XSS attacks
 * Converts special characters to HTML entities
 * 
 * @param {string} text - Text to escape
 * @returns {string} Escaped text safe for HTML insertion
 * 
 * @example
 * escapeHtml('<script>alert("XSS")</script>')
 * // Returns: '&lt;script&gt;alert("XSS")&lt;/script&gt;'
 */
export function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Sanitize HTML input by removing dangerous tags
 * Allows only safe formatting tags
 * 
 * @param {string} html - HTML to sanitize
 * @returns {string} Sanitized HTML
 */
export function sanitizeHtml(html) {
    const allowedTags = ['b', 'i', 'em', 'strong', 'p', 'br'];
    const div = document.createElement('div');
    div.innerHTML = html;
    
    // Remove all script tags and event handlers
    const scripts = div.querySelectorAll('script');
    scripts.forEach(script => script.remove());
    
    return div.innerHTML;
}

/**
 * Create a DOM element from HTML string
 * Useful for template string conversion
 * 
 * @param {string} htmlString - HTML string
 * @returns {HTMLElement} DOM element
 */
export function createElementFromHTML(htmlString) {
    const template = document.createElement('template');
    template.innerHTML = htmlString.trim();
    return template.content.firstChild;
}

/**
 * Debounce function execution
 * Prevents function from being called too frequently
 * 
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}
