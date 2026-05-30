import React from 'react';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

interface Props {
  step: number;
}

export const ProcessingTimeline: React.FC<Props> = ({ step }) => {
  const steps = [
    '等待操作',
    '已接收抖音风格链接，解析中...',
    '命中本地 fixture 映射，构建 VideoContentAsset...',
    '生成决策卡与召回历史资产...',
    '已保存为可回流资产'
  ];

  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
      <h3 className="text-sm font-bold text-slate-700 mb-4">资产化状态</h3>
      <div className="flex flex-col gap-3">
        {steps.map((text, index) => {
          const isCompleted = step > index;
          const isCurrent = step === index && step !== 0 && step !== steps.length - 1;
          
          return (
            <div key={index} className={`flex items-center gap-3 text-sm ${
              isCompleted ? 'text-indigo-600' : isCurrent ? 'text-blue-600 font-medium' : 'text-slate-400'
            }`}>
              {isCompleted ? (
                <CheckCircle2 size={18} />
              ) : isCurrent ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Circle size={18} />
              )}
              <span>{text}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
