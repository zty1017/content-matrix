import React from 'react';
import { DemoContext } from '../types';
import { Users } from 'lucide-react';

interface Props {
  contexts: DemoContext[];
  selectedContext: string;
  onChange: (contextId: string) => void;
}

export const DemoUserSwitcher: React.FC<Props> = ({ contexts, selectedContext, onChange }) => {
  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
      <div className="flex items-center gap-2 mb-4">
        <Users size={18} className="text-slate-500" />
        <h3 className="text-sm font-bold text-slate-700">切换用户上下文</h3>
      </div>
      <div className="flex flex-col gap-2">
        {contexts.map(ctx => (
          <button
            key={ctx.context_id}
            onClick={() => onChange(ctx.context_id)}
            className={`px-4 py-3 rounded-xl text-sm text-left transition-all ${
              selectedContext === ctx.context_id
                ? 'bg-indigo-50 border border-indigo-200 text-indigo-700 font-medium'
                : 'bg-slate-50 border border-transparent text-slate-600 hover:bg-slate-100'
            }`}
          >
            {ctx.name}
          </button>
        ))}
      </div>
    </div>
  );
};
