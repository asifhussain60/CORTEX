/**
 * SubTabs Component Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';

const fs = require('fs');
const path = require('path');
const subTabsCode = fs.readFileSync(
  path.join(__dirname, '../js/components/SubTabs.js'),
  'utf8'
);

describe('SubTabs Component', () => {
  let dom, document, SubTabs;
  
  beforeEach(() => {
    dom = new JSDOM(`
      <!DOCTYPE html>
      <html>
        <body>
          <div class="sub-tabs" id="test-subtabs">
            <div class="sub-tabs__list">
              <button class="sub-tab active" data-sub-tab="tab1">Tab 1</button>
              <button class="sub-tab" data-sub-tab="tab2">Tab 2</button>
              <button class="sub-tab" data-sub-tab="tab3">Tab 3</button>
            </div>
            <div class="sub-tab-panel active" data-sub-tab-panel="tab1">
              <p>Content 1</p>
            </div>
            <div class="sub-tab-panel" data-sub-tab-panel="tab2">
              <p>Content 2</p>
            </div>
            <div class="sub-tab-panel" data-sub-tab-panel="tab3">
              <p>Content 3</p>
            </div>
          </div>
        </body>
      </html>
    `);
    
    global.document = dom.window.document;
    global.window = dom.window;
    global.localStorage = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn()
    };
    
    eval(subTabsCode);
    SubTabs = global.SubTabs || (typeof module !== 'undefined' ? module.exports : null);
  });
  
  describe('SUBTAB-001: Initialization', () => {
    it('should create sub-tabs instance', () => {
      const subTabs = new SubTabs('#test-subtabs');
      expect(subTabs).toBeDefined();
    });
    
    it('should find all tabs', () => {
      const subTabs = new SubTabs('#test-subtabs');
      expect(subTabs.tabs.length).toBe(3);
    });
    
    it('should find all panels', () => {
      const subTabs = new SubTabs('#test-subtabs');
      expect(subTabs.panels.length).toBe(3);
    });
  });
  
  describe('SUBTAB-002: Switching', () => {
    it('should switch to tab by index', () => {
      const subTabs = new SubTabs('#test-subtabs', { saveState: false });
      subTabs.switchTo(1);
      expect(subTabs.getCurrentTab()).toBe(1);
    });
    
    it('should switch to tab by ID', () => {
      const subTabs = new SubTabs('#test-subtabs', { saveState: false });
      subTabs.switchTo('tab2');
      expect(subTabs.getCurrentTabId()).toBe('tab2');
    });
    
    it('should update active classes', () => {
      const subTabs = new SubTabs('#test-subtabs', { saveState: false });
      subTabs.switchTo(1);
      
      const tabs = document.querySelectorAll('.sub-tab');
      expect(tabs[1].classList.contains('active')).toBe(true);
      expect(tabs[0].classList.contains('active')).toBe(false);
    });
    
    it('should show correct panel', () => {
      const subTabs = new SubTabs('#test-subtabs', { saveState: false });
      subTabs.switchTo(1);
      
      const panels = document.querySelectorAll('.sub-tab-panel');
      expect(panels[1].classList.contains('active')).toBe(true);
      expect(panels[0].classList.contains('active')).toBe(false);
    });
  });
  
  describe('SUBTAB-003: Enable/Disable', () => {
    it('should disable tab', () => {
      const subTabs = new SubTabs('#test-subtabs', { saveState: false });
      subTabs.disable(1);
      expect(subTabs.tabs[1].enabled).toBe(false);
    });
    
    it('should enable tab', () => {
      const subTabs = new SubTabs('#test-subtabs', { saveState: false });
      subTabs.disable(1);
      subTabs.enable(1);
      expect(subTabs.tabs[1].enabled).toBe(true);
    });
    
    it('should switch away from disabled active tab', () => {
      const subTabs = new SubTabs('#test-subtabs', { saveState: false });
      subTabs.switchTo(1);
      subTabs.disable(1);
      expect(subTabs.getCurrentTab()).not.toBe(1);
    });
  });
  
  describe('SUBTAB-004: State Persistence', () => {
    it('should save state to localStorage', () => {
      const subTabs = new SubTabs('#test-subtabs', { 
        saveState: true,
        stateKey: 'test-key'
      });
      subTabs.switchTo(2);
      
      expect(localStorage.setItem).toHaveBeenCalledWith('test-key', '2');
    });
    
    it('should load saved state', () => {
      localStorage.getItem.mockReturnValue('1');
      
      const subTabs = new SubTabs('#test-subtabs', { 
        saveState: true,
        stateKey: 'test-key'
      });
      
      expect(subTabs.getCurrentTab()).toBe(1);
    });
    
    it('should clear saved state', () => {
      const subTabs = new SubTabs('#test-subtabs', { 
        saveState: true,
        stateKey: 'test-key'
      });
      subTabs.clearState();
      
      expect(localStorage.removeItem).toHaveBeenCalledWith('test-key');
    });
  });
  
  describe('SUBTAB-005: Callbacks', () => {
    it('should trigger onTabChange callback', () => {
      const onTabChange = vi.fn();
      const subTabs = new SubTabs('#test-subtabs', { 
        onTabChange,
        saveState: false
      });
      
      subTabs.switchTo(2);
      expect(onTabChange).toHaveBeenCalled();
    });
  });
});
