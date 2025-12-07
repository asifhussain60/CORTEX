export interface Task {
  id: number;
  title: string;
  isCompleted: boolean;
}

export interface CreateTaskRequest {
  title: string;
}

export interface UpdateTaskRequest {
  title: string;
  isCompleted: boolean;
}
