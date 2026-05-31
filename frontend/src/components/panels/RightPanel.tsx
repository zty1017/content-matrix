import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useCubeStore } from '../../store/useCubeStore';
import { useCabinetStore } from '../../store/useCabinetStore';
import type { CubeFaceId } from '../../types/api';

const accentColors = {
  cyan: 'text-cyan-600 bg-cyan-100/50 border-cyan-200',
  blue: 'text-blue-600 bg-blue-100/50 border-blue-200',
  violet: 'text-violet-600 bg-violet-100/50 border-violet-200',
  amber: 'text-amber-600 bg-amber-100/50 border-amber-200',
  red: 'text-red-600 bg-red-100/50 border-red-200',
  neutral: 'text-slate-600 bg-slate-100/50 border-slate-200',
};

const FACE_ORDER: CubeFaceId[] = [
  'primary_card',
  'related_assets',
  'snapshot',
  'evidence',
  'source',
  'inferences'
];

export const RightPanel: React.FC = () => {
  const { currentCubeView, selectedFaceId, setSelectedFaceId } = useCubeStore();
  const { saveCurrentToCabinet } = useCabinetStore();
  const [isSaving, setIsSaving] = useState(false);
  const [panelState, setPanelState] = useState<'expanded' | 'half' | 'collapsed'>('expanded');

  const isSelected = !!selectedFaceId;
  const displayFaceId: CubeFaceId = selectedFaceId || 'primary_card';
  const faceData = currentCubeView?.faces?.[displayFaceId];

  const handleSaveSnapshot = () => {
    if (!currentCubeView || isSaving) return;
    setIsSaving(true);
    
    saveCurrentToCabinet(currentCubeView);

    setTimeout(() => {
      setIsSaving(false);
      setSelectedFaceId(null);
    }, 1500);
  };

  const handleCopy = () => {
    if (faceData) {
      navigator.clipboard.writeText(faceData.summaryItems.join('\n'));
      // Could show a toast here
    }
  };

  const handleNavigate = (direction: 'prev' | 'next') => {
    const currentIndex = FACE_ORDER.indexOf(displayFaceId);
    let nextIndex = direction === 'next' ? currentIndex + 1 : currentIndex - 1;
    if (nextIndex < 0) nextIndex = FACE_ORDER.length - 1;
    if (nextIndex >= FACE_ORDER.length) nextIndex = 0;
    setSelectedFaceId(FACE_ORDER[nextIndex]);
  };

  if (panelState === 'collapsed') {
    return (
      <div className="absolute right-6 top-24 bottom-24 w-12 z-30 flex flex-col pointer-events-auto items-center py-4 glass-panel rounded-2xl cursor-pointer hover:bg-white/50 transition-colors" onClick={() => setPanelState('expanded')}>
        <span className="writing-vertical-rl text-slate-500 font-medium tracking-widest" style={{ writingMode: 'vertical-rl' }}>面板展开</span>
      </div>
    );
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: 100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="absolute right-6 top-24 bottom-24 w-80 z-30 flex flex-col pointer-events-auto"
      >
        {isSaving && (
          <motion.div 
            className="fixed z-50 w-16 h-16 bg-blue-400/80 backdrop-blur-md rounded-xl border border-white shadow-2xl shadow-blue-500/50 flex items-center justify-center text-white font-bold"
            initial={{ top: '50%', right: '400px', scale: 1 }}
            animate={{ top: '150px', right: 'calc(100vw - 300px)', scale: 0.3, opacity: 0 }}
            transition={{ duration: 1, ease: 'easeInOut' }}
          >
            保存中
          </motion.div>
        )}

        <div className="glass-panel h-full rounded-2xl flex flex-col overflow-hidden shadow-xl shadow-slate-200/50 border border-white/60">
          
          <div className="px-5 py-4 border-b border-white/50 bg-white/30 backdrop-blur-md relative">
            <div className="absolute right-4 top-4 flex gap-2">
              <button onClick={() => setPanelState(panelState === 'expanded' ? 'half' : 'expanded')} className="text-slate-400 hover:text-slate-700 text-sm">
                {panelState === 'expanded' ? '折叠' : '展开'}
              </button>
              <button onClick={() => setPanelState('collapsed')} className="text-slate-400 hover:text-slate-700 text-sm">
                收起
              </button>
              {isSelected && (
                <button 
                  onClick={() => setSelectedFaceId(null)}
                  className="text-slate-400 hover:text-slate-700 text-sm ml-2"
                >
                  ✕ 概览
                </button>
              )}
            </div>
            <h2 className="text-lg font-bold text-slate-800 tracking-wide mt-1">
              {faceData ? faceData.label : '解析概览'}
            </h2>
            
            <div className="absolute right-4 bottom-4 flex gap-1">
              <button 
                onClick={() => handleNavigate('prev')}
                className="w-7 h-7 flex items-center justify-center rounded-full bg-white/50 hover:bg-white/80 text-slate-500 hover:text-slate-700 transition-colors shadow-sm border border-white"
              >
                <ChevronLeft size={16} />
              </button>
              <button 
                onClick={() => handleNavigate('next')}
                className="w-7 h-7 flex items-center justify-center rounded-full bg-white/50 hover:bg-white/80 text-slate-500 hover:text-slate-700 transition-colors shadow-sm border border-white"
              >
                <ChevronRight size={16} />
              </button>
            </div>

            <div className="flex items-center gap-2 mt-2">
              <span className={`px-2 py-0.5 text-xs font-medium rounded border ${faceData ? accentColors[faceData.accent] : accentColors.neutral}`}>
                {faceData ? faceData.status.replace('_', ' ').toUpperCase() : 'READY'}
              </span>
              {faceData?.needsConfirmation && (
                <span className="px-2 py-0.5 text-xs font-medium rounded border border-amber-300 text-amber-600 bg-amber-50">
                  待确认
                </span>
              )}
            </div>
          </div>

          <div className="flex-1 p-5 overflow-y-auto space-y-4 scrollbar-hide">
            {faceData ? (
              <>
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold text-slate-500">关键摘要</h3>
                  
                  {faceData.id === 'source' && (
                    <div className="w-full aspect-video bg-slate-200 rounded-xl overflow-hidden relative mb-3 shadow-inner flex items-center justify-center">
                      <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
                      <span className="text-white font-medium z-10 flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-white/30 backdrop-blur-md flex items-center justify-center">
                          ▶
                        </div>
                        视频预览
                      </span>
                    </div>
                  )}

                  <div className="glass-pill rounded-xl p-3 flex flex-col gap-2 bg-white/40">
                    {faceData.summaryItems.map((item, idx) => (
                      <div key={idx} className="text-sm text-slate-700 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                        {item}
                      </div>
                    ))}
                  </div>
                </div>

                {panelState === 'expanded' && (
                  <div className="pt-4 border-t border-white/40">
                    <h3 className="text-sm font-semibold text-slate-500 mb-3">相关操作</h3>
                    <div className="flex flex-col gap-2">
                      <button className="glass-button w-full py-2 rounded-lg text-sm font-medium text-blue-600 flex items-center justify-center gap-1">
                        <span>＋</span> 补充 / 修正内容
                      </button>
                      <button onClick={handleCopy} className="glass-button w-full py-2 rounded-lg text-sm font-medium text-slate-600 flex items-center justify-center gap-1">
                        复制卡片
                      </button>
                      {faceData.id === 'snapshot' && (
                        <button 
                          onClick={handleSaveSnapshot}
                          disabled={isSaving}
                          className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-md shadow-blue-500/20 hover:shadow-blue-500/40 transition-all w-full py-2 rounded-lg text-sm font-medium disabled:opacity-50 mt-2"
                        >
                          {isSaving ? '入柜中...' : '保存入柜'}
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-sm text-slate-500 flex items-center justify-center h-full">
                加载中...
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
