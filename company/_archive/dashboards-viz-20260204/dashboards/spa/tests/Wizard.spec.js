/**
 * Wizard Component Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';

// Load Wizard component
const fs = require('fs');
const path = require('path');
const wizardCode = fs.readFileSync(
  path.join(__dirname, '../js/components/Wizard.js'),
  'utf8'
);

describe('Wizard Component', () => {
  let dom, document, Wizard;
  
  beforeEach(() => {
    // Setup DOM
    dom = new JSDOM(`
      <!DOCTYPE html>
      <html>
        <body>
          <div class="wizard" id="test-wizard">
            <div class="wizard__step" data-step-title="Overview">
              <h2>Step 1</h2>
            </div>
            <div class="wizard__step" data-step-title="Configuration">
              <h2>Step 2</h2>
            </div>
            <div class="wizard__step" data-step-title="Review">
              <h2>Step 3</h2>
            </div>
          </div>
        </body>
      </html>
    `);
    
    global.document = dom.window.document;
    global.window = dom.window;
    
    // Evaluate Wizard code
    eval(wizardCode);
    Wizard = global.Wizard || (typeof module !== 'undefined' ? module.exports : null);
  });
  
  describe('WIZ-001: Initialization', () => {
    it('should create wizard instance', () => {
      const wizard = new Wizard('#test-wizard');
      expect(wizard).toBeDefined();
      expect(wizard.initialized).toBe(true);
    });
    
    it('should throw error for invalid container', () => {
      expect(() => new Wizard('#invalid')).toThrow();
    });
    
    it('should find all wizard steps', () => {
      const wizard = new Wizard('#test-wizard');
      expect(wizard.steps.length).toBe(3);
      expect(wizard.steps[0].title).toBe('Overview');
    });
  });
  
  describe('WIZ-002: Navigation', () => {
    it('should start on first step', () => {
      const wizard = new Wizard('#test-wizard');
      expect(wizard.getCurrentStep()).toBe(0);
    });
    
    it('should navigate to next step', () => {
      const wizard = new Wizard('#test-wizard');
      wizard.next();
      expect(wizard.getCurrentStep()).toBe(1);
    });
    
    it('should navigate to previous step', () => {
      const wizard = new Wizard('#test-wizard');
      wizard.next();
      wizard.previous();
      expect(wizard.getCurrentStep()).toBe(0);
    });
    
    it('should not go before first step', () => {
      const wizard = new Wizard('#test-wizard');
      wizard.previous();
      expect(wizard.getCurrentStep()).toBe(0);
    });
    
    it('should not go after last step', () => {
      const wizard = new Wizard('#test-wizard');
      wizard.goToStep(2);
      wizard.next();
      expect(wizard.getCurrentStep()).toBe(2);
    });
  });
  
  describe('WIZ-003: Breadcrumb', () => {
    it('should create breadcrumb navigation', () => {
      const wizard = new Wizard('#test-wizard');
      const breadcrumb = document.querySelector('.wizard__breadcrumb');
      expect(breadcrumb).toBeTruthy();
    });
    
    it('should show all steps in breadcrumb', () => {
      const wizard = new Wizard('#test-wizard');
      const items = document.querySelectorAll('.wizard__breadcrumb-item');
      expect(items.length).toBe(3);
    });
    
    it('should mark current step as active', () => {
      const wizard = new Wizard('#test-wizard');
      wizard.goToStep(1);
      const items = document.querySelectorAll('.wizard__breadcrumb-item');
      expect(items[1].classList.contains('active')).toBe(true);
    });
  });
  
  describe('WIZ-004: Callbacks', () => {
    it('should trigger onStepChange callback', () => {
      const onStepChange = vi.fn();
      const wizard = new Wizard('#test-wizard', { onStepChange });
      
      wizard.next();
      expect(onStepChange).toHaveBeenCalledWith({
        currentStep: 1,
        previousStep: 0,
        step: wizard.steps[1]
      });
    });
    
    it('should trigger onComplete callback', () => {
      const onComplete = vi.fn();
      const wizard = new Wizard('#test-wizard', { onComplete });
      
      wizard.goToStep(2);
      wizard.complete();
      expect(onComplete).toHaveBeenCalled();
    });
  });
  
  describe('WIZ-005: Validation', () => {
    it('should validate current step', () => {
      const wizard = new Wizard('#test-wizard');
      wizard.validateStep(false);
      
      const nextBtn = document.querySelector('[data-action="next"]');
      expect(nextBtn.disabled).toBe(true);
    });
    
    it('should enable navigation when valid', () => {
      const wizard = new Wizard('#test-wizard');
      wizard.validateStep(true);
      
      const nextBtn = document.querySelector('[data-action="next"]');
      expect(nextBtn.disabled).toBe(false);
    });
  });
  
  describe('WIZ-006: Reset', () => {
    it('should reset to first step', () => {
      const wizard = new Wizard('#test-wizard');
      wizard.goToStep(2);
      wizard.reset();
      expect(wizard.getCurrentStep()).toBe(0);
    });
    
    it('should clear visited flags', () => {
      const wizard = new Wizard('#test-wizard');
      wizard.goToStep(2);
      wizard.reset();
      expect(wizard.steps.every(s => !s.visited)).toBe(true);
    });
  });
});
