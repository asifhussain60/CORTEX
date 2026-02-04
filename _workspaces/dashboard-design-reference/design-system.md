# Dashboard Design System
**Source:** Git commit `fc2194696` (2026-02-01) | **Phase:** 18

## Color Palette (SSOT)

### Primary Colors
```css
:root {
  /* Dark Theme Backgrounds */
  --color-dark-bg: #0a1428;           /* Main dark background */
  --color-dark-secondary: #1a2a4a;    /* Secondary darker background */
  --glass-bg: rgba(10, 20, 40, 0.7);  /* Glass effect background */
  --glass-border: rgba(255, 255, 255, 0.1);  /* Glass border */
  
  /* Accent Colors (CORTEX Brand) */
  --accent-primary: #4d8cff;    /* Primary accent blue */
  --accent-light: #7fb3ff;      /* Light accent blue */
  --accent-dark: #0d6efd;       /* Dark accent blue */
  --accent-hover: #5a9cff;      /* Accent hover state */
  
  /* Text Colors (Light text on dark background) */
  --text-primary: rgba(255, 255, 255, 0.87);   /* Main text - WCAG AA compliant */
  --text-secondary: rgba(255, 255, 255, 0.7);  /* Secondary text */
  --text-tertiary: rgba(255, 255, 255, 0.5);   /* Tertiary text */
  --text-disabled: rgba(255, 255, 255, 0.3);   /* Disabled text */
  
  /* Status Colors */
  --status-success: #22c55e;    /* Green success */
  --status-warning: #f59e0b;    /* Orange warning */
  --status-danger: #ef4444;     /* Red danger */
  --status-info: #4d8cff;       /* Blue info */
  
  /* Border Colors */
  --border-subtle: rgba(255, 255, 255, 0.05);
  --border-normal: rgba(255, 255, 255, 0.1);
  --border-strong: rgba(255, 255, 255, 0.2);
}
```

## Glassmorphism Effects

### Glass Card Component
```css
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: 1.5rem;
  transition: all var(--transition-normal);
}

.glass-card:hover {
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}
```

### Accent Glass Card
```css
.glass-card-accent {
  background: linear-gradient(135deg,
    rgba(77, 140, 255, 0.1) 0%,
    rgba(10, 20, 40, 0.7) 100%);
  border: 1px solid var(--accent-primary);
  box-shadow: 0 0 20px rgba(77, 140, 255, 0.2), var(--shadow-md);
}

.glass-card-accent:hover {
  box-shadow: 0 0 30px rgba(77, 140, 255, 0.3), var(--shadow-lg);
}
```

## Border Radius Scale
```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
```

## Shadow Effects
```css
--shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
--shadow-md: 0 8px 32px rgba(0, 0, 0, 0.3);
--shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.4);
--shadow-xl: 0 24px 64px rgba(0, 0, 0, 0.5);
```

## Transitions
```css
--transition-fast: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
--transition-normal: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
```

## Typography
```css
html, body {
  font-family: 'Poppins', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: var(--color-dark-bg);
  color: var(--text-primary);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  background: linear-gradient(135deg, 
    var(--color-dark-bg) 0%, 
    var(--color-dark-secondary) 100%);
  min-height: 100vh;
}
```

## Button Styles
```css
.btn-primary {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-dark));
  color: white;
  border: none;
  border-radius: var(--radius-md);
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--accent-hover), var(--accent-primary));
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(77, 140, 255, 0.4);
}

.btn-glass {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}
```

## Tab Navigation
```css
.tab-navigation {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
}

.tab-button {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-weight: 500;
}

.tab-button:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.tab-button.active {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-dark));
  color: white;
  box-shadow: 0 0 15px rgba(77, 140, 255, 0.3);
}
```

## Table Styles
```css
.glass-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.glass-table th {
  background: rgba(77, 140, 255, 0.1);
  color: var(--accent-light);
  font-weight: 600;
  text-align: left;
  padding: 1rem;
  border-bottom: 1px solid var(--glass-border);
}

.glass-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-primary);
}

.glass-table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}
```

## Metric Cards
```css
.metric-card {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  text-align: center;
  transition: all var(--transition-normal);
}

.metric-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--accent-primary);
  margin-bottom: 0.5rem;
}

.metric-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-trend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  margin-top: 0.5rem;
  font-size: 0.875rem;
}

.metric-trend.positive { color: var(--status-success); }
.metric-trend.negative { color: var(--status-danger); }
```

## Status Badges
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-success {
  background: rgba(34, 197, 94, 0.2);
  color: var(--status-success);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.badge-warning {
  background: rgba(245, 158, 11, 0.2);
  color: var(--status-warning);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-danger {
  background: rgba(239, 68, 68, 0.2);
  color: var(--status-danger);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-info {
  background: rgba(77, 140, 255, 0.2);
  color: var(--status-info);
  border: 1px solid rgba(77, 140, 255, 0.3);
}
```

## Responsive Grid
```css
.grid-container {
  display: grid;
  gap: 1.5rem;
}

/* Desktop: 4 columns */
@media (min-width: 1200px) {
  .grid-4 { grid-template-columns: repeat(4, 1fr); }
  .grid-3 { grid-template-columns: repeat(3, 1fr); }
}

/* Tablet: 2 columns */
@media (min-width: 768px) and (max-width: 1199px) {
  .grid-4, .grid-3 { grid-template-columns: repeat(2, 1fr); }
}

/* Mobile: 1 column */
@media (max-width: 767px) {
  .grid-4, .grid-3 { grid-template-columns: 1fr; }
}
```

## Header with Logo Glow
```css
.dashboard-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--glass-border);
}

.logo {
  width: 60px;
  height: 60px;
  filter: drop-shadow(0 0 20px rgba(77, 140, 255, 0.5));
}

.dashboard-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
}

.dashboard-subtitle {
  font-size: 0.875rem;
  color: var(--text-secondary);
}
```

## Health Score Circle
```css
.health-score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: conic-gradient(
    var(--status-success) 0% 85%,
    rgba(255, 255, 255, 0.1) 85% 100%
  );
  position: relative;
}

.health-score-inner {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: var(--color-dark-bg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.health-score-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--status-success);
}
```

---

## Usage Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Dashboard</title>
    <style>
        /* Paste CSS variables and components above */
    </style>
</head>
<body>
    <header class="dashboard-header">
        <img src="assets/cortex-logo.png" class="logo" alt="CORTEX">
        <div>
            <h1 class="dashboard-title">Repository Intelligence</h1>
            <p class="dashboard-subtitle">Enterprise Dashboard</p>
        </div>
    </header>
    
    <nav class="tab-navigation">
        <button class="tab-button active">Overview</button>
        <button class="tab-button">Architecture</button>
        <button class="tab-button">Vulnerabilities</button>
        <!-- More tabs -->
    </nav>
    
    <main class="dashboard-container">
        <div class="grid-container grid-4">
            <div class="metric-card">
                <div class="metric-value">85%</div>
                <div class="metric-label">Health Score</div>
            </div>
            <!-- More cards -->
        </div>
    </main>
</body>
</html>
```

---

*Design Authority: company/dashboards/kashkole/dashboard.html*
*Implementation: DashboardThemeTemplate class (670 lines)*
