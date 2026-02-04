/**
 * Vitest Test Setup
 * Global test configuration and mocks
 */

import { vi } from 'vitest';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;

// Mock ECharts
global.echarts = {
  init: vi.fn(() => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
  })),
  graphic: {
    LinearGradient: vi.fn((x1, y1, x2, y2, colors) => ({
      x: x1, y: y1, x2, y2, colors
    })),
  },
};

// Mock Mermaid
global.mermaid = {
  initialize: vi.fn(),
  render: vi.fn((id, definition) => 
    Promise.resolve({
      svg: `<svg id="${id}"><text>${definition}</text></svg>`
    })
  ),
};

// Mock Fuse.js
global.Fuse = vi.fn().mockImplementation((data, options) => ({
  search: vi.fn((query) => 
    data.filter(item => JSON.stringify(item).includes(query))
      .map((item, idx) => ({ item, refIndex: idx }))
  ),
}));

// Setup DOM before each test
beforeEach(() => {
  document.body.innerHTML = '';
  vi.clearAllMocks();
});

// Cleanup after each test
afterEach(() => {
  document.body.innerHTML = '';
});
