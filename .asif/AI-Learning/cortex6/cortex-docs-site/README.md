# CORTEX Documentation Site (GitHub Pages)

This is a modern documentation website for the CORTEX application, designed to be hosted on **GitHub Pages**.

## Local dev

```bash
npm install
npm run start
```

## Build

```bash
npm run build
```

## Deploy (GitHub Pages)

A GitHub Actions workflow is included at `.github/workflows/deploy.yml`.

1. In your repo settings, enable Pages and set Source to **GitHub Actions**.
2. Push to `main` (or update the workflow branch).
3. The workflow builds and deploys to GitHub Pages.

## Notes

- Mermaid diagrams are supported in MDX.
- Content is derived from the `cortex6/source-of-truth` specifications (governance + architecture + diagrams).
