import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAppStore } from '../../store/useAppStore';
import workshopBlocksData from '../../data/workshopBlocks.json';
import type { WorkshopBlock } from '../../types/workshop';

export const WorkshopView: React.FC = () => {
  const { setMode, currentDemoContext } = useAppStore();
  const [targetQuery, setTargetQuery] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const blocks: WorkshopBlock[] = (workshopBlocksData as any)[currentDemoContext] || (workshopBlocksData as any)['food_decision'];

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      setMode('current'); 
    }, 2500);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="absolute inset-0 top-16 bg-slate-50/95 backdrop-blur-3xl z-20 flex flex-col p-6 overflow-hidden"
    >
      <header className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setMode('current')}
            className="w-10 h-10 glass-pill flex items-center justify-center text-slate-500 hover:text-blue-600 transition-colors"
          >
            ←
          </button>
          <h2 className="text-xl font-bold text-slate-700 tracking-wide">魔方工坊 <span className="text-sm font-normal text-slate-400 ml-2">多资产重构台</span></h2>
        </div>
        <div className="flex gap-3">
          <button className="glass-button px-4 py-2 text-sm font-medium text-slate-600 rounded-lg">
            保存草稿
          </button>
        </div>
      </header>

      <div className="flex-1 flex gap-6 min-h-0">
        
        <div className="w-64 glass-panel rounded-2xl p-4 flex flex-col overflow-y-auto scrollbar-hide">
          <h3 className="text-sm font-bold text-slate-500 mb-4 uppercase tracking-widest">参与资产 (3)</h3>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="glass-button p-3 rounded-xl border border-white/60 relative">
                <div className="w-8 h-8 absolute -left-3 -top-3 bg-blue-100 rounded border border-blue-200 flex items-center justify-center text-xs font-bold text-blue-600 shadow-sm transform -rotate-6">
                  {i}
                </div>
                <p className="text-sm font-medium text-slate-700 ml-3">资产来源 {i}</p>
                <p className="text-xs text-slate-400 ml-3 mt-1">包含 {Math.floor(Math.random()*5)+2} 个核心块</p>
              </div>
            ))}
          </div>
          <button className="mt-4 border border-dashed border-slate-300 text-slate-400 rounded-xl py-3 text-sm hover:border-blue-400 hover:text-blue-500 transition-colors">
            + 拖入更多资产
          </button>
        </div>

        <div className="flex-1 glass-panel rounded-2xl relative flex flex-col items-center justify-center overflow-hidden border border-white/80 shadow-[inset_0_0_50px_rgba(255,255,255,0.5)]">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-400/5 rounded-full blur-3xl"></div>
          
          <div className="absolute top-6 left-6 text-sm font-bold text-slate-500 uppercase tracking-widest">
            内容块拆解池
          </div>

          <div className="relative w-full h-full max-w-2xl max-h-96">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 rounded-2xl bg-white/40 border border-white shadow-[0_0_30px_rgba(56,189,248,0.2)] backdrop-blur-md flex items-center justify-center z-10">
              <span className="text-blue-500 font-bold text-center">新魔方<br/>胚胎</span>
            </div>

            {blocks.map((block, i) => {
              const angle = (i / blocks.length) * Math.PI * 2;
              const radius = 180;
              const x = Math.cos(angle) * radius;
              const y = Math.sin(angle) * radius;

              return (
                <motion.div 
                  key={block.id}
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1, x: `calc(-50% + ${x}px)`, y: `calc(-50% + ${y}px)` }}
                  transition={{ delay: i * 0.1, type: 'spring' }}
                  className="absolute top-1/2 left-1/2 w-40 glass-pill p-3 border border-white/80 shadow-md cursor-pointer hover:scale-105 transition-transform"
                >
                  <div className="text-[10px] text-blue-500 font-bold mb-1">{block.type}</div>
                  <div className="text-xs text-slate-700 line-clamp-2">{block.content}</div>
                </motion.div>
              );
            })}
          </div>
        </div>

        <div className="w-80 flex flex-col gap-4">
          <div className="glass-panel rounded-2xl p-5 border border-white/60 shadow-lg flex-1">
            <h3 className="text-sm font-bold text-slate-500 mb-4 uppercase tracking-widest">生成目标策略</h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-600 block mb-2">输出风格模板</label>
                <div className="flex flex-wrap gap-2">
                  {['决策建议', '知识解释', '脚本复用', '精简卡片'].map(tpl => (
                    <span key={tpl} className="px-3 py-1.5 text-xs rounded-full border border-blue-200 bg-blue-50 text-blue-600 cursor-pointer hover:bg-blue-100">
                      {tpl}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-600 block mb-2">一句话指令</label>
                <textarea 
                  value={targetQuery}
                  onChange={(e) => setTargetQuery(e.target.value)}
                  placeholder="例如：结合排队经验，给我一个明确的去或不去的决策..."
                  className="w-full h-24 bg-white/50 border border-slate-200 rounded-xl p-3 text-sm outline-none resize-none focus:border-blue-400 focus:bg-white transition-colors"
                />
              </div>
            </div>
          </div>

          <button 
            onClick={handleGenerate}
            disabled={isGenerating}
            className="w-full py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-500 text-white font-bold text-lg shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:transform-none flex items-center justify-center gap-2"
          >
            {isGenerating ? (
              <><span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> 融合中...</>
            ) : (
              '生成新资产魔方'
            )}
          </button>
        </div>

      </div>
    </motion.div>
  );
};
