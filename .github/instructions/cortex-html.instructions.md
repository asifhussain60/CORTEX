---
applyTo: "docs/**/*.html"
---

# CORTEX Documentation HTML Rules

**These rules apply when editing HTML files under `docs/`.**

## Content Rules
- No Python code in `docs/` — documentation is HTML/CSS only
- No `.md` report files — all content is inline HTML
- Images served from `docs/assets/` — never external URLs without approval

## Accessibility (a11y)
- All images MUST have `alt` attributes
- Use semantic HTML: `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`
- Color contrast ratio ≥ 4.5:1 for body text
- Interactive elements must be keyboard-accessible

## CSS Standards
- Use CSS custom properties (variables) for theming: `--cortex-primary`, `--cortex-bg`
- Mobile-first responsive design — breakpoints at 768px and 1024px
- No inline styles — use external stylesheets in `docs/assets/css/`

## Performance
- Lazy-load images below the fold: `loading="lazy"`
- Minify CSS for production
- No JavaScript frameworks — vanilla JS only if needed
