import type { DashboardData } from '../types/dashboard';

const API_BASE_URL = 'https://your-domain.com';

export async function fetchDashboardData(): Promise<DashboardData> {
  const response = await fetch(`${API_BASE_URL}/api/dashboard`);

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const result = await response.json();

  if (!result?.success || !result?.data) {
    throw new Error('Invalid dashboard payload');
  }

  return result.data as DashboardData;
}
