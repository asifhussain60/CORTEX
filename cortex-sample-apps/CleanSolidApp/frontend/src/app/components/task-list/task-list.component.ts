import { Component, OnInit } from '@angular/core';
import { TaskService } from '../../services/task.service';
import { TaskItem } from '../../models/task.model';

@Component({
  selector: 'app-task-list',
  templateUrl: './task-list.component.html'
})
export class TaskListComponent implements OnInit {
  tasks: TaskItem[] = [];
  newTitle = '';
  filter = '';

  constructor(private taskService: TaskService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.taskService.getTasks(this.filter).subscribe(tasks => this.tasks = tasks);
  }

  create(): void {
    if (!this.newTitle.trim()) return;
    this.taskService.createTask(this.newTitle)
      .subscribe(() => {
        this.newTitle = '';
        this.load();
      });
  }

  toggle(task: TaskItem): void {
    this.taskService.updateStatus(task.id, !task.isCompleted)
      .subscribe(() => this.load());
  }

  delete(task: TaskItem): void {
    this.taskService.deleteTask(task.id)
      .subscribe(() => this.load());
  }
}
