#!/bin/bash
# Phase 3 Batch Sed Replacements
# Fixes all remaining Level 2 pages with inline styles

cd /Users/asifhussain/PROJECTS/CORTEX

echo "Starting Phase 3 batch cleanup..."

# Color badges
find docs -name "*.html" -type f ! -name "index.html" -exec sed -i '' \
  -e 's/style="background: #E91E63;"/class="level2-badge-pink"/g' \
  -e 's/style="background: #4CAF50;"/class="level2-badge-green"/g' \
  -e 's/style="background: #10b981;"/class="level2-badge-green-alt"/g' \
  -e 's/style="background: #f44336;"/class="level2-badge-red"/g' \
  -e 's/style="background: #FF9800;"/class="level2-badge-orange"/g' \
  -e 's/style="background: #3b82f6;"/class="level2-badge-blue"/g' \
  -e 's/style="background: #7b61ff;"/class="level2-badge-purple"/g' \
  {} +

# Text utilities
find docs -name "*.html" -type f ! -name "index.html" -exec sed -i '' \
  -e 's/style="color: var(--accent-primary);"/class="level2-text-accent"/g' \
  -e 's/style="color: var(--text-secondary); margin-bottom: 1rem;"/class="level2-text-muted-mb"/g' \
  -e 's/style="color: var(--text-secondary); margin-bottom: 1.5rem;"/class="level2-text-muted-mb-lg"/g' \
  -e 's/style="text-align: center; color: var(--text-secondary); margin-bottom: 1.5rem;"/class="level2-text-center-muted"/g' \
  -e 's/style="color: var(--text-secondary); max-width: 800px; margin: 1rem auto; line-height: 1.8;"/class="level2-text-muted-prose"/g' \
  -e 's/style="margin: 0; color: #aaa;"/class="level2-text-muted-0"/g' \
  -e 's/style="margin-top: 0; color: #10b981;"/class="level2-text-success-mt0"/g' \
  {} +

# Layout utilities
find docs -name "*.html" -type f ! -name "index.html" -exec sed -i '' \
  -e 's/style="text-align: center; padding: 3rem;"/class="level2-text-center-padded"/g' \
  -e 's/style="margin-top: 1.5rem; font-size: 0.875rem;"/class="level2-text-sm-mt"/g' \
  -e 's/style="font-size: 0.875rem;"/class="level2-text-xs"/g' \
  -e 's/style="max-width: 600px; margin: 0 auto 2rem;"/class="level2-container-centered"/g' \
  -e 's/style="margin-bottom: 1.5rem;"/class="level2-mb-lg"/g' \
  -e 's/style="margin-top: 1rem;"/class="level2-mt-md"/g' \
  -e 's/style="min-width: 220px; text-align: center;"/class="level2-card-min-width"/g' \
  {} +

# Complex utilities
find docs -name "*.html" -type f ! -name "index.html" -exec sed -i '' \
  -e 's/style="display: flex; justify-content: space-between; align-items: center;"/class="level2-flex-between"/g' \
  -e 's/style="background: rgba(0, 0, 0, 0.3); padding: 2rem; border-radius: 8px;"/class="level2-dark-panel-lg"/g' \
  -e 's/style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px;"/class="level2-dark-panel-md"/g' \
  -e 's/style="list-style: none; padding: 0; margin-top: 0.5rem;"/class="level2-list-clean"/g' \
  -e 's/style="width: 100%; margin-top: 1rem;"/class="level2-width-full-mt"/g' \
  {} +

# CTA button
find docs -name "*.html" -type f ! -name "index.html" -exec sed -i '' \
  -e 's/style="display: inline-block; padding: 1rem 2rem; background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)); border-radius: 8px; text-decoration: none; transition: all 0.3s;"/class="level2-cta-primary"/g' \
  {} +

echo "Batch cleanup complete!"
echo ""
echo "Checking results..."
python3 tests/scan_level2_pages.py
