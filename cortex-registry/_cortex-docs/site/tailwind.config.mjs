/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        'cortex-primary': '#4CAF50',
        'cortex-secondary': '#2196F3',
        'cortex-accent': '#FF9800',
        'cortex-dark': '#1a1a1a',
        'cortex-darker': '#0d0d0d',
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
  darkMode: 'class',
}
