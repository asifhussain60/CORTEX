// ✅ SMELL-21 FIXED: Report list extracted into own component
// ✅ SMELL-18 FIXED: textContent — no innerHTML XSS risk

import type { Report } from '../models/models.js';

export function renderReports(container: HTMLElement, reports: Report[]): void {
  container.replaceChildren();

  if (reports.length === 0) {
    const empty = document.createElement('p');
    empty.textContent = 'No reports found.';
    container.appendChild(empty);
    return;
  }

  for (const r of reports) {
    const card = document.createElement('div');
    card.className = 'report-card';

    const title = document.createElement('h4');
    title.textContent = r.title;

    const content = document.createElement('p');
    content.textContent = r.content;

    const meta = document.createElement('small');
    meta.textContent = `Generated: ${new Date(r.generatedAt).toLocaleString()}`;

    card.appendChild(title);
    card.appendChild(content);
    card.appendChild(meta);
    container.appendChild(card);
  }
}
