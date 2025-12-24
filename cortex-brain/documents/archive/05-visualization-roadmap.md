# CORTEX Lens v3.0 - Visualization Replacement Roadmap (Mermaid → D3.js)

**Version:** 1.0  
**Date:** December 14, 2025  
**Phase:** Phase 0 - Planning & Preparation  
**Status:** Roadmap Defined

---

## 🎯 Objective

Replace Mermaid.js diagrams with comprehensive D3.js visualization stack for better interactivity, performance, and zero external dependencies.

---

## 📊 Current State (v2.5)

**Mermaid.js Usage in CORTEX Lens v2.5:**
- Architecture diagrams (flowcharts)
- Dependency graphs (basic node-edge)
- Limited interactivity (static SVG output)
- External CDN dependency

**Limitations:**
- Static diagrams (no zoom/pan/drag)
- Limited styling control
- Performance issues with large graphs (>100 nodes)
- No real-time data updates
- CDN dependency violates zero-dep requirement

---

## 🚀 Target State (v3.0)

**D3.js Visualization Stack:**
- 6 D3.js custom visualizations
- Full interactivity (zoom, pan, drag, click, hover)
- Canvas rendering for large datasets
- Real-time updates
- Export to PNG/SVG
- Zero external dependencies (vendored D3.js)

---

## 🗺️ Visualization Replacement Matrix

| Visualization | v2.5 (Mermaid) | v3.0 (D3.js) | Complexity | Sub-Plan |
|---------------|----------------|--------------|------------|----------|
| **Architecture Diagram** | Flowchart | Custom Component Layout | HIGH | SP-4 |
| **Dependency Graph** | Graph | Force-Directed Layout | HIGH | SP-4 |
| **File Hierarchy** | Not implemented | Tree/Hierarchy | MEDIUM | SP-4 |
| **LOC Distribution** | Bar chart | Sunburst Diagram | MEDIUM | SP-4 |
| **Module Interactions** | Not implemented | Chord Diagram | HIGH | SP-4 |
| **3D Brain** | Not in v2.5 | Three.js (separate) | HIGH | SP-1 |

---

## 📐 D3.js Visualization Specifications

### 1. Architecture Diagram (Component Layout)

**Purpose:** Visualize application architecture with layers (UI → BLL → DAL)

**D3.js Technique:** Custom force simulation with layer constraints

**Features:**
- Component nodes (rectangles with labels)
- Connections (arrows showing dependencies)
- Layer positioning (vertical stacking)
- Color coding by responsibility (UI=blue, BLL=green, DAL=orange)
- Zoom/pan
- Click to show component details

**Data Structure:**
```json
{
  "nodes": [
    {"id": "UserController", "layer": "UI", "type": "Controller"},
    {"id": "UserService", "layer": "BLL", "type": "Service"},
    {"id": "UserRepository", "layer": "DAL", "type": "Repository"}
  ],
  "links": [
    {"source": "UserController", "target": "UserService"},
    {"source": "UserService", "target": "UserRepository"}
  ]
}
```

**Implementation:**
- File: `src/cortex_lens/templates/base/visualizations/d3-architecture-diagram.js`
- LOC: ~200
- Dependencies: D3.js force, zoom, drag

---

### 2. Dependency Graph (Force-Directed Layout)

**Purpose:** Visualize package/module dependencies with clustering

**D3.js Technique:** Force-directed graph with collision detection

**Features:**
- Nodes = packages/modules (circles sized by LOC)
- Edges = import relationships (arrows)
- Clustering by domain (color-coded groups)
- Collision detection (prevent overlap)
- Zoom/pan/drag
- Hover for dependency details
- Filter by package type (direct vs transitive)

**Data Structure:**
```json
{
  "nodes": [
    {"id": "flask", "group": "framework", "loc": 10000, "type": "direct"},
    {"id": "werkzeug", "group": "framework", "loc": 5000, "type": "transitive"}
  ],
  "links": [
    {"source": "flask", "target": "werkzeug", "strength": 50}
  ]
}
```

**Implementation:**
- File: `src/cortex_lens/templates/base/visualizations/d3-dependency-graph.js`
- LOC: ~250
- Dependencies: D3.js force, zoom, drag, collision

---

### 3. File Hierarchy (Tree Diagram)

**Purpose:** Visualize directory structure with file type icons

**D3.js Technique:** Collapsible tree layout

**Features:**
- Expandable/collapsible nodes
- File type icons (folder, .py, .js, .css, etc.)
- LOC count per file (tooltip)
- Complexity indicators (color-coded)
- Breadcrumb navigation
- Search/filter

**Data Structure:**
```json
{
  "name": "src",
  "type": "folder",
  "children": [
    {"name": "app.py", "type": "file", "loc": 500, "complexity": "medium"},
    {"name": "utils", "type": "folder", "children": [...]}
  ]
}
```

**Implementation:**
- File: `src/cortex_lens/templates/base/visualizations/d3-hierarchy-tree.js`
- LOC: ~200
- Dependencies: D3.js hierarchy, tree

---

### 4. LOC Distribution (Sunburst Diagram)

**Purpose:** Visualize LOC distribution by directory hierarchy

**D3.js Technique:** Sunburst (radial partition)

**Features:**
- Inner ring = top-level directories
- Outer rings = nested structure
- Size = LOC count (arc angle)
- Color = file type or complexity
- Click to zoom into subdirectory
- Breadcrumb showing current path

**Data Structure:**
```json
{
  "name": "root",
  "value": 10000,
  "children": [
    {"name": "src", "value": 8000, "children": [...]},
    {"name": "tests", "value": 2000, "children": [...]}
  ]
}
```

**Implementation:**
- File: `src/cortex_lens/templates/base/visualizations/d3-sunburst.js`
- LOC: ~180
- Dependencies: D3.js partition, arc

---

### 5. Module Interactions (Chord Diagram)

**Purpose:** Visualize inter-module dependencies and coupling

**D3.js Technique:** Chord diagram

**Features:**
- Circular layout (modules on perimeter)
- Arc thickness = coupling strength
- Hover to highlight connections
- Color-coded by module domain
- Bidirectional relationships

**Data Structure:**
```json
{
  "modules": ["UI", "BLL", "DAL", "Utils"],
  "matrix": [
    [0, 10, 5, 2],  // UI → others
    [8, 0, 15, 3],  // BLL → others
    [0, 12, 0, 1],  // DAL → others
    [5, 3, 2, 0]    // Utils → others
  ]
}
```

**Implementation:**
- File: `src/cortex_lens/templates/base/visualizations/d3-chord-diagram.js`
- LOC: ~220
- Dependencies: D3.js chord, ribbon, arc

---

### 6. 3D Brain (Three.js - Separate)

**Purpose:** Rotating 3D brain showing system health

**Technique:** Three.js (not D3.js, but part of viz stack)

**Features:**
- Rotating brain mesh (IcosahedronGeometry)
- Health score color coding (red → yellow → green)
- Particle effects (optional)
- Interactive rotation controls

**Implementation:**
- File: `src/cortex_lens/templates/base/visualizations/three-brain-3d.js`
- LOC: ~200
- Dependencies: Three.js (vendored)

---

## 📦 D3.js Vendoring Strategy

**Zero Dependencies Requirement:**
- Download D3.js v7 minified (~250 KB)
- Place in `src/cortex_lens/templates/base/vendor/d3.v7.min.js`
- Load via `<script src="vendor/d3.v7.min.js"></script>`
- No CDN, no npm install

**Three.js Vendoring:**
- Download Three.js r150 minified (~600 KB)
- Place in `src/cortex_lens/templates/base/vendor/three.r150.min.js`
- Load via `<script src="vendor/three.r150.min.js"></script>`

**Chart.js Vendoring:**
- Download Chart.js v4 minified (~200 KB)
- Place in `src/cortex_lens/templates/base/vendor/chart.v4.min.js`
- For simple bar/line/pie charts (less interactive than D3)

---

## 🎨 Common Features Across All Visualizations

1. **Zoom/Pan:**
   ```javascript
   const zoom = d3.zoom()
     .scaleExtent([0.5, 5])
     .on('zoom', (event) => {
       svg.attr('transform', event.transform);
     });
   svg.call(zoom);
   ```

2. **Drag:**
   ```javascript
   const drag = d3.drag()
     .on('start', dragstarted)
     .on('drag', dragged)
     .on('end', dragended);
   nodes.call(drag);
   ```

3. **Tooltip:**
   ```javascript
   const tooltip = d3.select('body').append('div')
     .attr('class', 'tooltip')
     .style('opacity', 0);
   
   nodes.on('mouseover', (event, d) => {
     tooltip.html(`<strong>${d.name}</strong><br/>LOC: ${d.loc}`)
       .style('opacity', 1);
   });
   ```

4. **Export to PNG:**
   ```javascript
   function exportToPNG() {
     const svgElement = document.querySelector('svg');
     const canvas = document.createElement('canvas');
     const ctx = canvas.getContext('2d');
     const svgString = new XMLSerializer().serializeToString(svgElement);
     const img = new Image();
     img.onload = () => {
       canvas.width = img.width;
       canvas.height = img.height;
       ctx.drawImage(img, 0, 0);
       canvas.toBlob((blob) => {
         const url = URL.createObjectURL(blob);
         const a = document.createElement('a');
         a.href = url;
         a.download = 'visualization.png';
         a.click();
       });
     };
     img.src = 'data:image/svg+xml;base64,' + btoa(svgString);
   }
   ```

---

## 🚦 Migration Workflow

### Phase 1: Vendor D3.js/Three.js (Day 1)
- [ ] Download D3.js v7.min.js
- [ ] Download Three.js r150.min.js
- [ ] Download Chart.js v4.min.js
- [ ] Place in `vendor/` directory
- [ ] Test loading in HTML template

### Phase 2: Create Visualization Components (Day 2-4)
- [ ] Architecture diagram (200 LOC)
- [ ] Dependency graph (250 LOC)
- [ ] File hierarchy tree (200 LOC)
- [ ] LOC sunburst (180 LOC)
- [ ] Module chord diagram (220 LOC)
- [ ] 3D brain (200 LOC)

### Phase 3: Test with Real Data (Day 4-5)
- [ ] Test with 10K LOC repository
- [ ] Test with 100K LOC repository
- [ ] Test performance (render time <1s)
- [ ] Test interactions (zoom, pan, drag, click)
- [ ] Test export functionality

### Phase 4: Integration (Day 5)
- [ ] Integrate into templates (8 tabs)
- [ ] Add visualization selection logic
- [ ] Update documentation
- [ ] Create usage examples

---

## ✅ Success Criteria

Visualization replacement complete when:
- [ ] All 6 visualizations implemented
- [ ] D3.js/Three.js vendored (zero external deps)
- [ ] All visualizations render with real data
- [ ] Zoom/pan/drag working on all interactive viz
- [ ] Export to PNG/SVG functional
- [ ] Performance targets met (<1s render, <200ms interaction)
- [ ] No Mermaid.js code remains in codebase

---

**Next Action:** Begin implementation in Phase 2 (Sub-Plan 4)
