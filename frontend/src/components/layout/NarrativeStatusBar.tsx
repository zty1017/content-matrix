import React from 'react';
import { useCubeStore } from '../../store/useCubeStore';

export const NarrativeStatusBar: React.FC = () => {
  const { narrativeStage } = useCubeStore();

  const stages = [
    { id: 'source_resolution', label: '来源识别' },
    { id: 'content_reconstruction', label: '内容拆解' },
    { id: 'matrix_linking', label: '资产增强' },
    { id: 'final_form', label: '魔方成型' },
  ];

  const activeIndex = stages.findIndex(s => s.id === narrativeStage) >= 0 ? stages.findIndex(s => s.id === narrativeStage) : 0;

  return (
    <div className="absolute top-20 left-1/2 -translate-x-1/2 z-40 flex items-center gap-2">
      {stages.map((stage, index) => {
        const isPast = index < activeIndex;
        const isActive = index === activeIndex;
        
        return (
          <React.Fragment key={stage.id}>
            <div className={`glass-pill px-4 py-1.5 text-xs font-medium transition-all duration-500 flex items-center gap-2 ${
              isActive ? 'text-blue-600 bg-white shadow-[0_0_15px_rgba(59,130,246,0.15)] ring-1 ring-blue-400/30' : 
              isPast ? 'text-slate-500' : 'text-slate-400 bg-white/20'
            }`}>
              {isPast && <span className="text-emerald-500">✓</span>}
              {isActive && <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>}
              {stage.label}
            </div>
            {index < stages.length - 1 && (
              <div className={`w-4 h-[1px] transition-colors duration-500 ${isPast ? 'bg-blue-300' : 'bg-slate-300'}`} />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
