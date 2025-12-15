# CORTEX Lens v3.0 - Three.js 3D Brain Implementation Guide

**Phase:** 1 (Foundation)  
**Date:** December 14, 2025  
**Status:** Implementation Ready

---

## 📋 Overview

This guide documents the Three.js 3D brain visualization implementation from the admin dashboard and provides instructions for integrating it into CORTEX Lens v3.0.

**Source Location:** `cortex-brain/dashboards/ui/js/brain-3d.js`  
**Target Location:** `src/cortex_lens/static/js/brain-3d.js`

---

## 🧠 Current Implementation (Admin Dashboard)

### Architecture

```
brain-3d.js
├── BrainVisualizer class
│   ├── constructor(containerId, data)
│   ├── init() - Setup Three.js scene
│   ├── createBrain() - Generate brain geometry
│   ├── createNodes() - Neural nodes (spheres)
│   ├── createConnections() - Neural connections (lines)
│   ├── animate() - Render loop
│   ├── handleResize() - Responsive canvas
│   └── cleanup() - Memory management
```

### Dependencies

```javascript
// Three.js (vendored, no CDN)
import * as THREE from './vendor/three.min.js';
import { OrbitControls } from './vendor/OrbitControls.js';
```

**File Sizes:**
- `three.min.js`: ~600KB
- `OrbitControls.js`: ~20KB

### Key Features

1. **Brain Mesh**
   - Icosahedron geometry (detail level 2)
   - Glassmorphism material (transparent blue)
   - Wireframe overlay

2. **Neural Nodes**
   - ~50 sphere geometries
   - Random positions within brain volume
   - Pulsing animation (scale oscillation)

3. **Neural Connections**
   - Line segments connecting nearby nodes
   - Fading opacity based on distance
   - Max connection distance: 2 units

4. **Camera & Controls**
   - Perspective camera (FOV 75°)
   - OrbitControls (zoom, rotate, pan)
   - Auto-rotation: 0.001 rad/frame

5. **Lighting**
   - Ambient light (0xffffff, intensity 0.5)
   - Directional light (0xffffff, intensity 0.8)
   - Point light (0x3b82f6, intensity 1.0)

---

## 🎨 Glassmorphism Styling

### Brain Material

```javascript
const brainMaterial = new THREE.MeshPhysicalMaterial({
  color: 0x3b82f6,           // Primary blue
  transparent: true,
  opacity: 0.15,             // 15% opacity
  roughness: 0.1,
  metalness: 0.5,
  clearcoat: 1.0,
  clearcoatRoughness: 0.1,
  transmission: 0.8,         // Glass-like transmission
  ior: 1.5,                  // Index of refraction
  thickness: 0.5,
  side: THREE.DoubleSide
});
```

### Wireframe Overlay

```javascript
const wireframeMaterial = new THREE.LineBasicMaterial({
  color: 0x60a5fa,           // Primary light blue
  transparent: true,
  opacity: 0.3,
  linewidth: 1
});
```

### Node Material

```javascript
const nodeMaterial = new THREE.MeshBasicMaterial({
  color: 0x10b981,           // Accent green
  transparent: true,
  opacity: 0.8
});
```

### Connection Material

```javascript
const connectionMaterial = new THREE.LineBasicMaterial({
  color: 0x8b5cf6,           // Secondary purple
  transparent: true,
  opacity: 0.2,
  linewidth: 1
});
```

---

## 🔧 Integration Steps

### 1. Vendor Three.js (No CDN)

```bash
# Download Three.js r150 (600KB)
cd src/cortex_lens/static/vendor/
wget https://cdn.jsdelivr.net/npm/three@0.150.0/build/three.min.js

# Download OrbitControls (20KB)
wget https://cdn.jsdelivr.net/npm/three@0.150.0/examples/js/controls/OrbitControls.js
```

### 2. Copy brain-3d.js

```bash
cp cortex-brain/dashboards/ui/js/brain-3d.js \
   src/cortex_lens/static/js/brain-3d.js
```

### 3. Update Import Paths

**From (Admin):**
```javascript
import * as THREE from '/static/vendor/three.min.js';
import { OrbitControls } from '/static/vendor/OrbitControls.js';
```

**To (Lens):**
```javascript
import * as THREE from '../vendor/three.min.js';
import { OrbitControls } from '../vendor/OrbitControls.js';
```

### 4. HTML Container

```html
<!-- In your template -->
<div id="brain-container" style="width: 100%; height: 600px;"></div>

<script type="module">
  import { BrainVisualizer } from './static/js/brain-3d.js';
  
  // Sample data (replace with real metrics)
  const brainData = {
    nodes: 50,
    connections: 120,
    activity: 0.75
  };
  
  const brain = new BrainVisualizer('brain-container', brainData);
  brain.init();
</script>
```

### 5. CSS Styling

```css
#brain-container {
  width: 100%;
  height: 600px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
}

#brain-container canvas {
  display: block;
  width: 100%;
  height: 100%;
}
```

---

## 🎯 Customization Options

### Adjust Brain Size

```javascript
// In createBrain()
const geometry = new THREE.IcosahedronGeometry(
  2.5,  // Radius (default: 2.0)
  2     // Detail level (0-4)
);
```

### Change Node Count

```javascript
// In createNodes()
const nodeCount = 75;  // Default: 50
```

### Modify Connection Distance

```javascript
// In createConnections()
const maxDistance = 3.0;  // Default: 2.0
```

### Adjust Animation Speed

```javascript
// In animate()
this.brain.rotation.y += 0.002;  // Default: 0.001
```

### Color Customization

Use CORTEX Lens v3.0 color variables:

```javascript
// Brain material
color: parseInt(getComputedStyle(document.documentElement)
  .getPropertyValue('--color-primary').replace('#', ''), 16)

// Nodes
color: parseInt(getComputedStyle(document.documentElement)
  .getPropertyValue('--color-accent').replace('#', ''), 16)

// Connections
color: parseInt(getComputedStyle(document.documentElement)
  .getPropertyValue('--color-secondary').replace('#', ''), 16)
```

---

## 📊 Performance Considerations

### Memory Management

```javascript
// Cleanup when component unmounts
brain.cleanup();

// Inside cleanup()
cleanup() {
  this.scene.traverse((object) => {
    if (object.geometry) object.geometry.dispose();
    if (object.material) {
      if (Array.isArray(object.material)) {
        object.material.forEach(mat => mat.dispose());
      } else {
        object.material.dispose();
      }
    }
  });
  
  this.renderer.dispose();
  window.removeEventListener('resize', this.handleResize);
}
```

### Responsive Rendering

```javascript
// Adjust quality based on device
const isMobile = window.innerWidth < 768;
const pixelRatio = isMobile ? 1 : Math.min(window.devicePixelRatio, 2);
this.renderer.setPixelRatio(pixelRatio);
```

### Frame Rate Throttling

```javascript
// Limit to 30fps on low-end devices
let lastFrame = 0;
const targetFPS = 30;
const frameInterval = 1000 / targetFPS;

animate() {
  requestAnimationFrame(this.animate.bind(this));
  
  const now = Date.now();
  const delta = now - lastFrame;
  
  if (delta > frameInterval) {
    lastFrame = now - (delta % frameInterval);
    this.renderer.render(this.scene, this.camera);
  }
}
```

---

## ✅ Testing Checklist

### Visual Tests (Selenium)

- [ ] Canvas renders without errors
- [ ] Brain mesh visible with glassmorphism
- [ ] Neural nodes appear and pulse
- [ ] Connections drawn between nodes
- [ ] OrbitControls functional (zoom, rotate)
- [ ] Auto-rotation smooth
- [ ] Responsive to window resize

### Performance Tests

- [ ] Initial render < 500ms
- [ ] Frame rate ≥ 30fps
- [ ] Memory usage < 100MB
- [ ] No memory leaks after cleanup
- [ ] Smooth on mobile devices

### Integration Tests

- [ ] Loads in all templates (console_app, api_service, etc.)
- [ ] Works with Lens glassmorphism theme
- [ ] Colors match CSS variables
- [ ] No console errors
- [ ] Graceful fallback if WebGL unavailable

---

## 🚀 Future Enhancements (Phase 2-3)

### Phase 2: Interactivity

- Click nodes to show metrics tooltip
- Hover connections to highlight data flow
- Filter nodes by activity level
- Animate connections based on real-time data

### Phase 3: Data Integration

- Connect to Tier 2 knowledge graph
- Visualize module relationships
- Show file dependency paths
- Real-time conversation flow

### Phase 4: Advanced Features

- VR/AR support
- Neural network training visualization
- Time-travel replay of codebase evolution
- Multi-brain comparison (before/after)

---

## 📚 Resources

**Three.js Documentation:**  
- https://threejs.org/docs/
- https://threejs.org/examples/

**OrbitControls:**  
- https://threejs.org/docs/#examples/en/controls/OrbitControls

**WebGL Performance:**  
- https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices

**Glassmorphism in 3D:**  
- Three.js MeshPhysicalMaterial: https://threejs.org/docs/#api/en/materials/MeshPhysicalMaterial

---

## 🐛 Troubleshooting

### Canvas Not Rendering

```javascript
// Check WebGL support
if (!window.WebGLRenderingContext) {
  console.error('WebGL not supported');
  // Show fallback static image
}
```

### Performance Issues

```javascript
// Reduce detail level
const geometry = new THREE.IcosahedronGeometry(2.0, 1); // Detail 1 instead of 2

// Reduce node count
const nodeCount = 25; // Instead of 50
```

### Memory Leaks

```javascript
// Always call cleanup on unmount
window.addEventListener('beforeunload', () => {
  brain.cleanup();
});
```

---

**Next Step:** Execute extraction scripts and verify Three.js vendored files exist.
