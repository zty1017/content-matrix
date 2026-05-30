import React, { useEffect, useState } from 'react';
import { api } from '../api/api';

interface Asset {
  title?: string;
  asset_id?: string;
  [key: string]: unknown;
}

interface Snapshot {
  snapshot_id?: string;
  task_id?: string;
  [key: string]: unknown;
}

export const AssetLibrary: React.FC = () => {
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);

  useEffect(() => {
    // Fetch snapshots
    api.getSnapshots().then(res => {
      const list = Array.isArray(res) ? res : res.snapshots || [];
      setSnapshots(list);
    }).catch(e => console.error(e));

    // Fetch assets
    api.searchAssets().then(res => {
      const list = Array.isArray(res) ? res : res.assets || [];
      setAssets(list);
    }).catch(e => console.error(e));
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-6 font-sans">
      <div className="max-w-7xl mx-auto flex flex-col gap-6">
        <header className="mb-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
            资产库与快照 (Asset Library)
          </h1>
          <a href="/" className="text-sm text-indigo-600 hover:underline">返回主演示页</a>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
            <h2 className="text-lg font-bold mb-4">已保存的资产</h2>
            {assets.length === 0 ? (
              <p className="text-sm text-slate-500">暂无资产（或无法连接到后端）</p>
            ) : (
              <div className="flex flex-col gap-4">
                {assets.map((a, i) => (
                  <div key={i} className="p-3 bg-slate-50 border border-slate-100 rounded-xl">
                    <h3 className="font-bold text-sm">{String(a.title || a.asset_id || '')}</h3>
                    <p className="text-xs text-slate-500 mt-1">{JSON.stringify(a).substring(0, 100)}...</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
            <h2 className="text-lg font-bold mb-4">决策卡快照</h2>
            {snapshots.length === 0 ? (
              <p className="text-sm text-slate-500">暂无快照（或无法连接到后端）</p>
            ) : (
              <div className="flex flex-col gap-4">
                {snapshots.map((s, i) => (
                  <div key={i} className="p-3 bg-slate-50 border border-slate-100 rounded-xl">
                    <h3 className="font-bold text-sm">{String(s.snapshot_id || s.task_id || '')}</h3>
                    <p className="text-xs text-slate-500 mt-1">{JSON.stringify(s).substring(0, 100)}...</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
