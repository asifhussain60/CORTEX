/**
 * HTML Contract Tests - Validate dashboard.html structure
 * 
 * These tests run against the actual HTML file to ensure:
 * 1. Required container IDs exist
 * 2. Tab panels have correct aria attributes
 * 3. Data script tag is present
 * 
 * Uses JSDOM for fast execution (<100ms)
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';

describe('Dashboard HTML Contract', () => {
  let dom, document;
  
  beforeAll(() => {
    const htmlPath = path.join(__dirname, '..', 'dashboard.html');
    const html = fs.readFileSync(htmlPath, 'utf-8');
    dom = new JSDOM(html, {
      url: 'http://localhost:8888/dashboard.html?repo=KSESSIONS',
      contentType: 'text/html',
      includeNodeLocations: true
    });
    document = dom.window.document;
  });
  
  describe('Data Loading Infrastructure', () => {
    it('should have dashboard-data script tag', () => {
      const script = document.getElementById('dashboard-data');
      expect(script).toBeTruthy();
      expect(script.type).toBe('application/json');
    });
    
    it('should have DualFormatDataLoader script loaded', () => {
      const scripts = Array.from(document.querySelectorAll('script[src]'));
      const hasDataLoader = scripts.some(s => s.src.includes('DualFormatDataLoader'));
      expect(hasDataLoader).toBe(true);
    });
  });
  
  describe('Required Container IDs (from app.js references)', () => {
    const requiredContainers = [
      { id: 'vulnerabilities-list', purpose: 'Security vulnerabilities rendering' },
      { id: 'vuln-types-list', purpose: 'Vulnerability types summary' },
      { id: 'code-smells-grid', purpose: 'Quality code smells rendering' },
      { id: 'license-summary', purpose: 'Dependencies license summary' },
      { id: 'key-findings-list', purpose: 'Overview key findings' },
    ];
    
    requiredContainers.forEach(({ id, purpose }) => {
      it(`should have #${id} container (${purpose})`, () => {
        const el = document.getElementById(id);
        expect(el, `Missing container: ${id}`).toBeTruthy();
      });
    });
  });
  
  describe('Chart Containers', () => {
    const chartContainers = [
      'health-gauge',
      'coverage-gauge',
      'security-severity-chart',
      'code-quality-chart',
      'license-chart',
      'language-chart'
    ];
    
    chartContainers.forEach(id => {
      it(`should have #${id} chart container`, () => {
        const el = document.getElementById(id);
        expect(el, `Missing chart container: ${id}`).toBeTruthy();
      });
    });
  });
  
  describe('Tab Structure', () => {
    it('should have 13 tab buttons', () => {
      const tabs = document.querySelectorAll('[role="tab"]');
      expect(tabs.length).toBeGreaterThanOrEqual(13);
    });
    
    it('should have corresponding tab panels for each tab', () => {
      const tabs = document.querySelectorAll('[role="tab"]');
      
      tabs.forEach(tab => {
        const panelId = tab.getAttribute('aria-controls');
        expect(panelId).toBeTruthy();
        
        const panel = document.getElementById(panelId);
        expect(panel, `Tab "${tab.textContent.trim()}" missing panel #${panelId}`).toBeTruthy();
        expect(panel.getAttribute('role')).toBe('tabpanel');
      });
    });
    
    it('should have correct aria-labelledby relationships', () => {
      const panels = document.querySelectorAll('[role="tabpanel"]');
      
      panels.forEach(panel => {
        const tabId = panel.getAttribute('aria-labelledby');
        expect(tabId).toBeTruthy();
        
        const tab = document.getElementById(tabId);
        expect(tab, `Panel #${panel.id} references missing tab #${tabId}`).toBeTruthy();
        expect(tab.getAttribute('role')).toBe('tab');
      });
    });
  });
  
  describe('Component Integration', () => {
    it('should have wizard containers for Architecture tab', () => {
      const wizardSteps = document.querySelectorAll('[data-wizard-step]');
      // Architecture tab should have wizard steps
      expect(wizardSteps.length).toBeGreaterThan(0);
    });
    
    it('should have sub-tabs for Code Explorer', () => {
      const subTabs = document.querySelectorAll('.sub-tab-button');
      // Code Explorer should have sub-tabs
      expect(subTabs.length).toBeGreaterThan(0);
    });
  });
  
  describe('Script Loading Order', () => {
    it('should load data layer before app.js', () => {
      const scripts = Array.from(document.querySelectorAll('script[src]'));
      const dataLayerIndex = scripts.findIndex(s => s.src.includes('DualFormatDataLoader'));
      const appIndex = scripts.findIndex(s => s.src.includes('app.js'));
      
      expect(dataLayerIndex).toBeGreaterThan(-1);
      expect(appIndex).toBeGreaterThan(-1);
      expect(dataLayerIndex).toBeLessThan(appIndex);
    });
    
    it('should load components before chart initialization', () => {
      const scripts = Array.from(document.querySelectorAll('script[src]'));
      const wizardIndex = scripts.findIndex(s => s.src.includes('Wizard.js'));
      const chartIndex = scripts.findIndex(s => s.src.includes('ChartFactory'));
      
      if (wizardIndex > -1 && chartIndex > -1) {
        expect(wizardIndex).toBeLessThan(chartIndex);
      }
    });
  });
  
  describe('Error Handling UI', () => {
    it('should have app-container for error display', () => {
      const container = document.querySelector('.app-container');
      expect(container).toBeTruthy();
    });
  });
});
