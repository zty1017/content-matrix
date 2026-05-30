import React from 'react';
import { RelatedAsset } from '../types';
import { InfluenceTypeBadge } from './InfluenceTypeBadge';
import { Link } from 'lucide-react';

interface Props {
  asset: RelatedAsset;
}

export const RelatedAssetCard: React.FC<Props> = ({ asset }) => {
  const is07Asset = asset.asset_id?.includes('07') || asset.title?.includes('重庆');
  const coverUrl = is07Asset ? '/assets/covers/07-旅行-朋友你没时间去纽约-总有时间去重庆吧-cover.jpg' : null;

  return (
    <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 flex gap-3">
      {coverUrl && (
        <div className="w-16 h-24 shrink-0 rounded-lg overflow-hidden bg-slate-200">
          <img src={coverUrl} alt="Cover" className="w-full h-full object-cover" />
        </div>
      )}
      <div className="flex-1 flex flex-col">
        <div className="flex justify-between items-start mb-2 gap-2">
          <h4 className="text-sm font-bold text-slate-800 flex items-center gap-1 line-clamp-2">
            <Link size={14} className="text-indigo-500 shrink-0" />
            {asset.title}
          </h4>
          <InfluenceTypeBadge type={asset.influence_type} />
        </div>
        <p className="text-xs text-slate-600 bg-white p-2 rounded-lg border border-slate-100">
          {asset.explanation}
        </p>
      </div>
    </div>
  );
};
