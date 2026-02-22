// ✅ SMELL-21 FIXED: User table extracted into own component
// ✅ SMELL-18 FIXED: textContent instead of innerHTML — XSS eliminated
// ✅ SMELL-22 FIXED: Typed User interface

import type { User } from '../models/models.js';

export function renderUsers(
  container: HTMLElement,
  users: User[],
  onDelete: (id: number) => Promise<void>
): void {
  container.replaceChildren();

  if (users.length === 0) {
    const empty = document.createElement('p');
    empty.textContent = 'No users found.';
    container.appendChild(empty);
    return;
  }

  const table = document.createElement('table');
  const thead = document.createElement('thead');
  const hr = document.createElement('tr');
  for (const h of ['ID', 'Username', 'Email', 'Role', 'Active', 'Actions']) {
    const th = document.createElement('th');
    th.textContent = h;
    hr.appendChild(th);
  }
  thead.appendChild(hr);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  for (const u of users) {
    const row = document.createElement('tr');
    const cells = [String(u.id), u.userName, u.email, u.role, u.isActive ? 'Yes' : 'No'];
    for (const val of cells) {
      const td = document.createElement('td');
      td.textContent = val;
      row.appendChild(td);
    }

    const actionTd = document.createElement('td');
    const btn = document.createElement('button');
    btn.textContent = 'Delete';
    btn.type = 'button';
    btn.addEventListener('click', () => {
      // ✅ SMELL-25 FIXED: Confirmation dialog before destructive action
      if (window.confirm(`Delete user "${u.userName}"? This cannot be undone.`)) {
        void onDelete(u.id);
      }
    });
    actionTd.appendChild(btn);
    row.appendChild(actionTd);
    tbody.appendChild(row);
  }

  table.appendChild(tbody);
  container.appendChild(table);
}
