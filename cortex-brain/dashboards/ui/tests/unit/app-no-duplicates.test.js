/**
 * Test: app.js should not have duplicate function declarations
 * 
 * This test verifies that functions imported from shared-utils.js
 * are not re-declared in app.js
 * 
 * Expected to FAIL initially due to duplicate showLoading/hideLoading
 */

import { describe, it, expect, beforeAll } from '@jest/globals';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

describe('app.js Duplicate Function Check (TDD RED Phase)', () => {
    let appJsContent;
    
    beforeAll(() => {
        const appJsPath = path.join(__dirname, '../../app.js');
        appJsContent = fs.readFileSync(appJsPath, 'utf-8');
    });
    
    it('should import showLoading from shared-utils.js', () => {
        expect(appJsContent).toMatch(/import\s+{[^}]*showLoading[^}]*}\s+from\s+['"]\.\/shared-utils\.js['"]/);
    });
    
    it('should import hideLoading from shared-utils.js', () => {
        expect(appJsContent).toMatch(/import\s+{[^}]*hideLoading[^}]*}\s+from\s+['"]\.\/shared-utils\.js['"]/);
    });
    
    it('should NOT have duplicate showLoading function declaration', () => {
        // Check for function declaration (not import)
        const functionDeclarations = appJsContent.match(/^function showLoading\s*\(/gm);
        
        expect(functionDeclarations).toBeNull(); // Should not exist since it's imported
    });
    
    it('should NOT have duplicate hideLoading function declaration', () => {
        // Check for function declaration (not import)
        const functionDeclarations = appJsContent.match(/^function hideLoading\s*\(/gm);
        
        expect(functionDeclarations).toBeNull(); // Should not exist since it's imported
    });
    
    it('should only have ONE occurrence of "function showLoading"', () => {
        // Count all occurrences (import line and function declarations)
        const allOccurrences = (appJsContent.match(/showLoading\s*\(/g) || []).length;
        
        // We expect: 1 import + usage calls (but NO function declaration)
        // Function declaration would add an extra occurrence
        const functionDeclarations = (appJsContent.match(/^function showLoading\s*\(/gm) || []).length;
        
        expect(functionDeclarations).toBe(0); // No function declarations allowed
    });
    
    it('should only have ONE occurrence of "function hideLoading"', () => {
        const functionDeclarations = (appJsContent.match(/^function hideLoading\s*\(/gm) || []).length;
        
        expect(functionDeclarations).toBe(0); // No function declarations allowed
    });
    
    it('should have showError function (app-specific, not imported)', () => {
        // showError is app-specific and should exist
        expect(appJsContent).toMatch(/^function showError\s*\(/m);
    });
    
    it('should have clearError function (app-specific, not imported)', () => {
        // clearError is app-specific and should exist
        expect(appJsContent).toMatch(/^function clearError\s*\(/m);
    });
});
