import React, { useEffect } from 'react';
import { useAppStore } from '../../store/useAppStore';

export const TopNav: React.FC = () => {
  const { currentMode, setMode, demoMode, setDemoMode, currentDemoContext, setDemoContext, apiStatus, testConnection } = useAppStore();

  const navItems = [
    { id: 'current', label: '当前魔方' },
    { id: 'cabinet', label: '资产陈列柜' },
    { id: 'workshop', label: '魔方工坊' },
  ] as const;

  const demoScenariosList = [
    { id: 'food_decision', label: '探店决策魔方' },
    { id: 'workplace_skit', label: '职场短剧拆解魔方' },
    { id: 'finance_knowledge', label: '财经知识解析魔方' }
  ];

  useEffect(() => {
    testConnection();
  }, [testConnection]);

  return (
    <header className="absolute top-0 left-0 right-0 h-16 z-50 flex items-center justify-between px-6 glass-panel border-b border-white/40">
      {/* Logo & Brand */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center shadow-inner text-white font-bold">
          CM
        </div>
        <span className="font-semibold text-slate-700 tracking-wide">Content Matrix</span>
      </div>

      {/* Main Navigation */}
      <nav className="flex items-center gap-2 glass-pill p-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setMode(item.id)}
            className={`px-5 py-1.5 rounded-full text-sm font-medium transition-all ${
              currentMode === item.id
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-slate-500 hover:text-slate-700 hover:bg-white/50'
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>

      {/* Demo Control Panel (Mini Version) */}
      <div className="flex items-center gap-3 text-sm">
        {/* Scenario Selection */}
        <select 
          value={currentDemoContext}
          onChange={(e) => setDemoContext(e.target.value)}
          className="bg-white/50 px-3 py-1.5 rounded-full border border-slate-200/50 outline-none text-slate-600 font-medium cursor-pointer"
        >
          {demoScenariosList.map(s => (
            <option key={s.id} value={s.id}>{s.label}</option>
          ))}
        </select>

        {/* Demo Mode Selection */}
        <div className="flex items-center gap-2 bg-slate-100/50 px-3 py-1.5 rounded-full border border-slate-200/50">
          <button 
            onClick={testConnection} 
            className="flex items-center gap-1 hover:opacity-80 transition-opacity"
            title={`API Status: ${apiStatus}`}
          >
            <span className={`w-2 h-2 rounded-full ${
              apiStatus === 'connected' ? 'bg-emerald-400' :
              apiStatus === 'testing' ? 'bg-amber-400 animate-pulse' :
              'bg-red-400'
            }`}></span>
          </button>
          <select 
            value={demoMode} 
            onChange={(e) => setDemoMode(e.target.value as any)}
            className="bg-transparent border-none outline-none text-slate-600 font-medium cursor-pointer"
          >
            <option value="prefer_backend">优先后端 API</option>
            <option value="force_fallback">强制 Fallback</option>
          </select>
        </div>
      </div>
    </header>
  );
};
