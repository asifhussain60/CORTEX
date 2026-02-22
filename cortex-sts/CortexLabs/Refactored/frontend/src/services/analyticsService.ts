import { apiClient } from '../api/apiClient';
import type { AnalyticsSummary } from '../models';
export const analyticsService = {
  getSummary: (userId: number) =>
    apiClient.get<AnalyticsSummary>(`/analytics/summary?userId=${userId}`),
};