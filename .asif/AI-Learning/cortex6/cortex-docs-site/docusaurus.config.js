/** @type {import('@docusaurus/types').Config} */
const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

module.exports = {
  title: 'CORTEX',
  tagline: 'The brain for GitHub Copilot — governance, orchestration, and multi-repo intelligence',
  favicon: 'img/favicon.svg',

  // GitHub Pages config (edit these for your repo)
  url: 'https://YOUR_GITHUB_USERNAME.github.io',
  baseUrl: '/YOUR_REPO_NAME/',
  organizationName: 'YOUR_GITHUB_USERNAME',
  projectName: 'YOUR_REPO_NAME',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: { defaultLocale: 'en', locales: ['en'] },

  presets: [
    [
      'classic',
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          routeBasePath: '/', // docs at site root
          editUrl: 'https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/edit/main/',
          showLastUpdateAuthor: false,
          showLastUpdateTime: true,
        },
        blog: {
          showReadingTime: true,
          routeBasePath: '/blog',
          editUrl: 'https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/edit/main/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  markdown: { mermaid: true },
  themes: ['@docusaurus/theme-mermaid'],

  themeConfig: {
    navbar: {
      title: 'CORTEX',
      items: [
        {to: '/', label: 'Docs', position: 'left'},
        {to: '/blog', label: 'Updates', position: 'left'},
        {
          href: 'https://github.com/asifhussain60/CORTEX',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Core',
          items: [
            { label: 'Overview', to: '/' },
            { label: 'Architecture', to: '/architecture/layers' },
            { label: 'Governance', to: '/governance/overview' },
          ],
        },
        {
          title: 'Orchestration',
          items: [
            { label: 'Master Orchestrator', to: '/orchestrators/master' },
            { label: 'TODO Orchestrator (DAG)', to: '/orchestrators/todo' },
            { label: 'Pattern Router (Trie)', to: '/orchestrators/pattern-router' },
          ],
        },
        {
          title: 'Multi‑Repo',
          items: [
            { label: 'MCP & Multi‑Repo', to: '/multi-repo/overview' },
            { label: 'Topology', to: '/multi-repo/topology' },
          ],
        },
      ],
      copyright:
        `Copyright © ${new Date().getFullYear()} Asif Hussain. Built with Docusaurus.`,
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
      additionalLanguages: ['python', 'yaml', 'bash', 'json'],
    },
    docs: {
      sidebar: { hideable: true },
    },
  },
};
