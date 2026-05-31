import { useAppStore } from '../store/useAppStore';

const TIMEOUT_MS = 5000;

const fetchWithTimeout = async (resource: string, options: RequestInit = {}) => {
  const { timeout = TIMEOUT_MS } = options as any;
  
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  const response = await fetch(resource, {
    ...options,
    signal: controller.signal
  });
  clearTimeout(id);

  return response;
};

const getBaseUrl = () => useAppStore.getState().apiBaseUrl;

export const checkHealth = async (): Promise<boolean> => {
  try {
    const res = await fetchWithTimeout(`${getBaseUrl()}/health`, { method: 'GET' });
    return res.ok;
  } catch {
    return false;
  }
};

export const apiCall = async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
  const { demoMode } = useAppStore.getState();
  
  if (demoMode === 'force_fallback') {
    throw new Error('Forced fallback mode enabled');
  }

  const isHealthy = await checkHealth();
  if (!isHealthy) {
    throw new Error('Backend is unreachable');
  }

  try {
    const response = await fetchWithTimeout(`${getBaseUrl()}${endpoint}`, options);
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    throw new Error(`API Call Failed: ${error}`);
  }
};

// Endpoints
export const resolveSource = (data: any) => apiCall('/api/v1/source/resolve', { method: 'POST', body: JSON.stringify(data) });
export const createTask = (data: any) => apiCall('/api/v1/tasks', { method: 'POST', body: JSON.stringify(data) });
export const getTaskCube = (taskId: string) => apiCall(`/api/v1/cube/tasks/${taskId}`, { method: 'GET' });
export const getTaskProgress = (taskId: string) => apiCall(`/api/v1/cube/tasks/${taskId}/progress`, { method: 'GET' });
export const generateCard = (taskId: string, data: any) => apiCall(`/api/v1/tasks/${taskId}/generate-card`, { method: 'POST', body: JSON.stringify(data) });
export const saveSnapshot = (taskId: string) => apiCall(`/api/v1/tasks/${taskId}/save-snapshot`, { method: 'POST' });
export const getSnapshots = () => apiCall('/api/v1/snapshots', { method: 'GET' });
export const parseLocalVideo = (data: any) => apiCall('/api/v1/local-video/parse', { method: 'POST', body: JSON.stringify(data) });
