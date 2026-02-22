// FIX SMELL-21: service layer separates API calls from UI logic
import { apiClient } from '../api/apiClient';
import type { User } from '../models';

export const userService = {
  list: (page = 1, pageSize = 20) =>
    apiClient.get<User[]>(`/users?page=${page}&pageSize=${pageSize}`),
  search: (username: string) =>
    apiClient.get<User>(`/users/search?username=${encodeURIComponent(username)}`),
  create: (user: Omit<User, 'id'>) => apiClient.post<User>('/users', user),
  delete: (id: number) => apiClient.delete(`/users/${id}`),
};