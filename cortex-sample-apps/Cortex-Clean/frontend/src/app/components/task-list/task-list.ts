import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService } from '../../services/task.service';
import { TaskStateService } from '../../services/task-state.service';
import { TaskItemComponent } from '../task-item/task-item';
import { TaskFormComponent } from '../task-form/task-form';
import { Task } from '../../models/task.model';

@Component({
  selector: 'app-task-list',
  imports: [CommonModule, FormsModule, TaskItemComponent, TaskFormComponent],
  templateUrl: './task-list.html',
  styleUrl: './task-list.scss'
})
export class TaskListComponent implements OnInit {
  tasks$;
  loading$;
  error$;
  
  filter = '';
  showForm = false;

  constructor(
    private taskService: TaskService,
    private taskState: TaskStateService
  ) {
    this.tasks$ = this.taskState.tasks$;
    this.loading$ = this.taskState.loading$;
    this.error$ = this.taskState.error$;
  }

  ngOnInit(): void {
    this.loadTasks();
  }

  loadTasks(): void {
    this.taskState.setLoading(true);
    this.taskService.getTasks(this.filter || undefined).subscribe({
      next: (tasks) => this.taskState.setTasks(tasks),
      error: (err) => this.taskState.setError(err.message || 'Failed to load tasks')
    });
  }

  onFilterChange(): void {
    this.loadTasks();
  }

  onToggle(id: number): void {
    this.taskService.toggleTask(id).subscribe({
      next: () => this.loadTasks(),
      error: (err) => this.taskState.setError(err.message || 'Failed to toggle task')
    });
  }

  onDelete(id: number): void {
    if (confirm('Are you sure you want to delete this task?')) {
      this.taskService.deleteTask(id).subscribe({
        next: () => this.loadTasks(),
        error: (err) => this.taskState.setError(err.message || 'Failed to delete task')
      });
    }
  }

  onTaskCreated(): void {
    this.showForm = false;
    this.loadTasks();
  }

  toggleForm(): void {
    this.showForm = !this.showForm;
  }
}
