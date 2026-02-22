// ══════════════════════════════════════════════════════════════════════════════
// Error Handler — Centralized error management
// ══════════════════════════════════════════════════════════════════════════════
// Fixes: SMELL-25b (no error handler utility → typed error classes)
// ══════════════════════════════════════════════════════════════════════════════

import { ApiError } from '../services/ApiClient';

/**
 * Display user-friendly error message in UI
 * @param error - Error object (any type)
 * @param containerId - DOM element ID to display error
 */
export function displayError(error: unknown, containerId: string): void {
  const container = document.getElementById(containerId);
  if (!container) return;

  let message = 'An unexpected error occurred';

  if (error instanceof ApiError) {
    message = `API Error (${error.statusCode}): ${error.message}`;
  } else if (error instanceof Error) {
    message = error.message;
  } else if (typeof error === 'string') {
    message = error;
  }

  container.innerHTML = `
    <div class="error-banner" style="background: #e74c3c; color: white; padding: 12px; border-radius: 4px; margin: 8px 0;">
      <strong>⚠️ Error:</strong> ${escapeHtml(message)}
    </div>
  `;
}

/**
 * Escape HTML to prevent XSS
 * @param unsafe - Untrusted string
 * @returns HTML-escaped string
 */
function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
