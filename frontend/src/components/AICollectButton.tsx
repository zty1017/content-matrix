import React from 'react';
import { Sparkles } from 'lucide-react';

interface Props {
  onClick: () => void;
  disabled?: boolean;
}

export const AICollectButton: React.FC<Props> = ({ onClick, disabled }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center justify-center gap-2 w-full py-4 rounded-xl font-bold text-white transition-all shadow-md ${
        disabled 
          ? 'bg-slate-300 cursor-not-allowed shadow-none' 
          : 'bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 hover:shadow-lg transform hover:-translate-y-0.5'
      }`}
    >
      <Sparkles size={20} />
      <span>AI 收藏 / 变成资产</span>
    </button>
  );
};
