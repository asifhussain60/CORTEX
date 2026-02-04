/**
 * Pagination Component Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';

const fs = require('fs');
const path = require('path');
const paginationCode = fs.readFileSync(
  path.join(__dirname, '../js/components/Pagination.js'),
  'utf8'
);

describe('Pagination Component', () => {
  let dom, document, Pagination;
  
  beforeEach(() => {
    dom = new JSDOM(`
      <!DOCTYPE html>
      <html>
        <body>
          <div id="test-pagination"></div>
        </body>
      </html>
    `);
    
    global.document = dom.window.document;
    global.window = dom.window;
    
    eval(paginationCode);
    Pagination = global.Pagination || (typeof module !== 'undefined' ? module.exports : null);
  });
  
  describe('PAG-001: Initialization', () => {
    it('should create pagination instance', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10
      });
      expect(pagination).toBeDefined();
    });
    
    it('should calculate total pages correctly', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 95,
        itemsPerPage: 10
      });
      expect(pagination.getTotalPages()).toBe(10);
    });
    
    it('should start on specified page', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10,
        currentPage: 3
      });
      expect(pagination.getCurrentPage()).toBe(3);
    });
  });
  
  describe('PAG-002: Navigation', () => {
    it('should navigate to specific page', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10
      });
      pagination.goToPage(5);
      expect(pagination.getCurrentPage()).toBe(5);
    });
    
    it('should not navigate to invalid page', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10
      });
      const currentPage = pagination.getCurrentPage();
      pagination.goToPage(20);
      expect(pagination.getCurrentPage()).toBe(currentPage);
    });
    
    it('should not navigate below page 1', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10
      });
      pagination.goToPage(0);
      expect(pagination.getCurrentPage()).toBe(1);
    });
  });
  
  describe('PAG-003: Page Size', () => {
    it('should change page size', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10
      });
      pagination.setPageSize(25);
      expect(pagination.getItemsPerPage()).toBe(25);
      expect(pagination.getTotalPages()).toBe(4);
    });
    
    it('should adjust current page when page size increases', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10
      });
      pagination.goToPage(8);
      pagination.setPageSize(25);
      expect(pagination.getCurrentPage()).toBe(4); // Adjusted down
    });
  });
  
  describe('PAG-004: Page Numbers Display', () => {
    it('should show all pages when total <= maxPages', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 50,
        itemsPerPage: 10,
        maxPages: 7
      });
      const pages = pagination._getPageNumbers();
      expect(pages).toEqual([1, 2, 3, 4, 5]);
    });
    
    it('should show ellipsis when total > maxPages', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 200,
        itemsPerPage: 10,
        maxPages: 7
      });
      pagination.goToPage(10);
      const pages = pagination._getPageNumbers();
      expect(pages.includes('...')).toBe(true);
    });
  });
  
  describe('PAG-005: Callbacks', () => {
    it('should trigger onPageChange callback', () => {
      const onPageChange = vi.fn();
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10,
        onPageChange
      });
      
      pagination.goToPage(3);
      expect(onPageChange).toHaveBeenCalledWith(
        expect.objectContaining({
          currentPage: 3,
          previousPage: 1,
          itemsPerPage: 10,
          startIndex: 20,
          endIndex: 29
        })
      );
    });
    
    it('should trigger callback on page size change', () => {
      const onPageChange = vi.fn();
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10,
        onPageChange
      });
      
      onPageChange.mockClear();
      pagination.setPageSize(25);
      expect(onPageChange).toHaveBeenCalled();
    });
  });
  
  describe('PAG-006: Update Total Items', () => {
    it('should update total items', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10
      });
      
      pagination.updateTotalItems(50);
      expect(pagination.getTotalPages()).toBe(5);
    });
    
    it('should adjust current page when total items decreases', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10
      });
      
      pagination.goToPage(10);
      pagination.updateTotalItems(25);
      expect(pagination.getCurrentPage()).toBe(3); // Adjusted
    });
  });
  
  describe('PAG-007: Rendering', () => {
    it('should render pagination controls', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10
      });
      
      const controls = document.querySelector('.pagination__controls');
      expect(controls).toBeTruthy();
    });
    
    it('should render page info', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10
      });
      
      const info = document.querySelector('.pagination__info');
      expect(info).toBeTruthy();
      expect(info.textContent).toContain('Showing 1 - 10 of 100');
    });
    
    it('should render page size selector when enabled', () => {
      const pagination = new Pagination('#test-pagination', {
        totalItems: 100,
        itemsPerPage: 10,
        showPageSize: true
      });
      
      const sizeSelect = document.querySelector('.pagination__size-select');
      expect(sizeSelect).toBeTruthy();
    });
  });
});
