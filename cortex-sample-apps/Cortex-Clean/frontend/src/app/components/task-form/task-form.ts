import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService } from '../../services/task.service';

@Component({
  selector: 'app-task-form',
  imports: [CommonModule, FormsModule],
  templateUrl: './task-form.html',
  styleUrl: './task-form.scss'
})
export class TaskFormComponent {
  @Output() taskCreated = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  title = '';
  submitting = false;
  error = '';

  constructor(private taskService: TaskService) {}

  onSubmit(): void {
    if (!this.title.trim()) {
      this.error = 'Title is required';
      return;
    }

    if (this.title.length > 255) {
      this.error = 'Title must be 255 characters or less';
      return;
    }

    this.submitting = true;
    this.error = '';

    this.taskService.createTask({ title: this.title.trim() }).subscribe({
      next: () => {
        this.title = '';
        this.submitting = false;
        this.taskCreated.emit();
      },
      error: (err) => {
        this.error = err.message || 'Failed to create task';
        this.submitting = false;
      }
    });
  }

  onCancel(): void {
    this.title = '';
    this.error = '';
    this.cancel.emit();
  }
}
