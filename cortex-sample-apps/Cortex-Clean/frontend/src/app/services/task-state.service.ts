import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Task } from '../models/task.model';

@Injectable({
  providedIn: 'root'
})
export class TaskStateService {
  private tasksSubject = new BehaviorSubject<Task[]>([]);
  private loadingSubject = new BehaviorSubject<boolean>(false);
  private errorSubject = new BehaviorSubject<string | null>(null);

  public tasks$: Observable<Task[]> = this.tasksSubject.asObservable();
  public loading$: Observable<boolean> = this.loadingSubject.asObservable();
  public error$: Observable<string | null> = this.errorSubject.asObservable();

  setTasks(tasks: Task[]): void {
    this.tasksSubject.next(tasks);
    this.errorSubject.next(null);
  }

  addTask(task: Task): void {
    const currentTasks = this.tasksSubject.value;
    this.tasksSubject.next([task, ...currentTasks]);
  }

  updateTask(id: number, updates: Partial<Task>): void {
    const currentTasks = this.tasksSubject.value;
    const index = currentTasks.findIndex(t => t.id === id);
    if (index !== -1) {
      currentTasks[index] = { ...currentTasks[index], ...updates };
      this.tasksSubject.next([...currentTasks]);
    }
  }

  removeTask(id: number): void {
    const currentTasks = this.tasksSubject.value;
    this.tasksSubject.next(currentTasks.filter(t => t.id !== id));
  }

  setLoading(loading: boolean): void {
    this.loadingSubject.next(loading);
  }

  setError(error: string | null): void {
    this.errorSubject.next(error);
    this.loadingSubject.next(false);
  }

  clearError(): void {
    this.errorSubject.next(null);
  }
}
