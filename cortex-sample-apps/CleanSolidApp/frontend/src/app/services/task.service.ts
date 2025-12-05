import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { TaskItem } from '../models/task.model';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private readonly baseUrl = 'https://localhost:5001/api/tasks';

  constructor(private http: HttpClient) {}

  getTasks(filter?: string): Observable<TaskItem[]> {
    const params: any = {};
    if (filter) params.filter = filter;
    return this.http.get<TaskItem[]>(this.baseUrl, { params });
  }

  createTask(title: string): Observable<TaskItem> {
    return this.http.post<TaskItem>(this.baseUrl, { title });
  }

  updateStatus(id: number, isCompleted: boolean): Observable<void> {
    return this.http.put<void>(`${this.baseUrl}/${id}`, { isCompleted });
  }

  deleteTask(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
