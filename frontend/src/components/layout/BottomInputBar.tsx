import React, { useState } from 'react';
import { runOneClickDemoSequence } from '../../lib/animationSequences';
import { useCubeStore } from '../../store/useCubeStore';
import { useAppStore } from '../../store/useAppStore';

export const BottomInputBar: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const { isAnimating } = useCubeStore();
  const { setAnimationSpeed } = useAppStore();

  const handleReconstruct = async () => {
    if (isAnimating) return;
    
    if (inputValue.trim() === 'demo') {
      await runOneClickDemoSequence();
    } else {
      await runOneClickDemoSequence(); 
    }
  };

  return (
    <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-40 w-full max-w-2xl">
      <div className="glass-panel rounded-2xl p-2 flex items-center gap-2 shadow-lg shadow-blue-900/5">
        <div className="flex-1 px-4 py-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isAnimating}
            placeholder="粘贴抖音链接 / 输入目标 / 拖入本地视频..."
            className="w-full bg-transparent outline-none text-slate-700 placeholder:text-slate-400 disabled:opacity-50"
            onKeyDown={(e) => e.key === 'Enter' && handleReconstruct()}
          />
        </div>
        <div className="w-px h-6 bg-slate-300/50 mx-2"></div>
        
        {isAnimating ? (
          <button 
            onClick={() => setAnimationSpeed('skip')}
            className="text-slate-500 text-sm font-medium px-4 hover:bg-slate-100 py-2 rounded-xl transition-colors"
          >
            跳过动画
          </button>
        ) : (
          <button 
            onClick={() => runOneClickDemoSequence()}
            className="text-slate-500 text-sm font-medium px-4 hover:bg-slate-100 py-2 rounded-xl transition-colors"
          >
            重播动画
          </button>
        )}

        <button 
          onClick={() => { setInputValue('demo'); runOneClickDemoSequence(); }}
          disabled={isAnimating}
          className="text-blue-600 text-sm font-medium px-4 hover:bg-blue-50 py-2 rounded-xl transition-colors disabled:opacity-50"
        >
          一键体验
        </button>

        <button 
          onClick={handleReconstruct}
          disabled={isAnimating}
          className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-400 text-white px-6 py-2 rounded-xl text-sm font-medium transition-colors shadow-sm shadow-blue-500/30"
        >
          {isAnimating ? '正在重构...' : '开始重构'}
        </button>
      </div>
    </div>
  );
};
