import React from 'react';
import { ReconstructionTaskData } from '../types';
import { RelatedAssetCard } from './RelatedAssetCard';

interface Props {
  data: ReconstructionTaskData;
}

export const DecisionCard: React.FC<Props> = ({ data }) => {
  const { primary_card, related_assets } = data;

  const getLevelColor = (level: string) => {
    if (level.includes('推荐') && !level.includes('不')) return 'bg-emerald-500';
    if (level.includes('谨慎') || level.includes('警告')) return 'bg-amber-500';
    if (level.includes('不建议')) return 'bg-rose-500';
    return 'bg-blue-500';
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col h-full">
      <div className="bg-slate-50 p-5 border-b border-slate-100 relative">
        <div className={`absolute top-0 left-0 w-1 h-full ${getLevelColor(primary_card.specific.decision_level)}`} />
        <div className="flex justify-between items-start gap-4">
          <h2 className="text-xl font-bold text-slate-800">{primary_card.common.title}</h2>
          <span className={`text-xs px-2 py-1 rounded-md text-white font-bold whitespace-nowrap ${getLevelColor(primary_card.specific.decision_level)}`}>
            {primary_card.specific.decision_level}
          </span>
        </div>
        <p className="text-sm text-slate-600 mt-2">{primary_card.common.summary}</p>
      </div>

      <div className="p-5 flex flex-col gap-6 flex-1 overflow-y-auto">
        <div>
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">一句话判断</h3>
          <p className="text-sm font-medium text-indigo-900 bg-indigo-50 p-3 rounded-xl border border-indigo-100">
            {primary_card.specific.one_sentence_judgement}
          </p>
        </div>

        {related_assets && related_assets.length > 0 && (
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">历史资产影响</h3>
            <div className="flex flex-col gap-2">
              {related_assets.map(asset => (
                <RelatedAssetCard key={asset.asset_id} asset={asset} />
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4">
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">关键因素</h3>
            <ul className="list-disc pl-4 text-sm text-slate-700 space-y-1">
              {primary_card.specific.key_factors.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          </div>
          {primary_card.specific.needs_confirmation.length > 0 && (
            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">待确认项</h3>
              <ul className="list-disc pl-4 text-sm text-slate-700 space-y-1">
                {primary_card.specific.needs_confirmation.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
