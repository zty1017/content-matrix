// /api/api.ts

const API_BASE = '/api/v1';

export const api = {
  async resolveSource(sourceUrl: string) {
    const res = await fetch(`${API_BASE}/source/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_type: 'douyin_url', source_url: sourceUrl }),
    });
    return res.json();
  },

  async buildAsset(resolvedSourceId: string) {
    const res = await fetch(`${API_BASE}/assets/build`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resolved_source_id: resolvedSourceId }),
    });
    return res.json();
  },

  async getDemoContexts() {
    const res = await fetch(`${API_BASE}/demo-contexts`);
    return res.json();
  },

  async getTask(taskId: string) {
    const res = await fetch(`${API_BASE}/tasks/${taskId}`);
    return res.json();
  },

  async saveSnapshot(taskId: string) {
    const res = await fetch(`${API_BASE}/tasks/${taskId}/save-snapshot`, {
      method: 'POST',
    });
    return res.json();
  },

  async getSnapshots() {
    const res = await fetch(`${API_BASE}/snapshots`);
    return res.json();
  },

  async searchAssets() {
    const res = await fetch(`${API_BASE}/assets/search`);
    return res.json();
  },
};
