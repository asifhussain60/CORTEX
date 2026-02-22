/**
 * Input validators — extracted from scattered inline checks (SMELL-07 fix).
 * Matches backend EmailValidator logic.
 */

const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

export function isValidEmail(email: string): boolean {
    return EMAIL_REGEX.test(email);
}

export function isPositiveNumber(value: unknown): value is number {
    return typeof value === 'number' && value > 0 && isFinite(value);
}

export function isNonEmptyString(value: unknown): value is string {
    return typeof value === 'string' && value.trim().length > 0;
}

/**
 * Sanitize user input for safe DOM insertion.
 * Prevents XSS when rendering dynamic content (SMELL-08 fix).
 */
export function escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
