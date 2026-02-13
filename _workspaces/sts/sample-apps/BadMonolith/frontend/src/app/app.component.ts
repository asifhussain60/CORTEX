import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  template: `
  <h1>BadMonolith Tasks</h1>
  <input [(ngModel)]="newTitle" placeholder="New task title" />
  <button (click)="create()">Create (direct API call)</button>
  <button (click)="load()">Load All</button>

  <ul>
    <li *ngFor="let t of tasks">
      <input type="checkbox" [checked]="t.isCompleted"
             (change)="toggle(t)" />
      {{t.title}} (id: {{t.id}})
      <button (click)="delete(t)">X</button>
    </li>
  </ul>
  `,
})
export class AppComponent {
  tasks: any[] = [];
  newTitle = '';
  apiUrl = 'http://localhost:5000/api/tasks';

  // Everything jammed into the component, no abstraction
  constructor(private http: HttpClient) {}

  load() {
    this.http.get<any[]>(this.apiUrl).subscribe(x => this.tasks = x);
  }

  create() {
    this.http.post(this.apiUrl, { title: this.newTitle }).subscribe(() => {
      this.load();
    });
  }

  toggle(t: any) {
    t.isCompleted = !t.isCompleted;
    this.http.put(this.apiUrl, { id: t.id, isCompleted: t.isCompleted }).subscribe();
  }

  delete(t: any) {
    this.http.delete(this.apiUrl + '?id=' + t.id).subscribe(() => this.load());
  }
}
