import React from 'react';
import { RelatedAsset } from '../types';
import { InfluenceTypeBadge } from './InfluenceTypeBadge';
import { Link } from 'lucide-react';

interface Props {
  asset: RelatedAsset;
}

export const RelatedAssetCard: React.FC<Props> = ({ asset }) => {
  return (
    <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
      <div className="flex justify-between items-start mb-2 gap-2">
        <h4 className="text-sm font-bold text-slate-800 flex items-center gap-1">
          <Link size={14} className="text-indigo-500" />
          {asset.title}
        </h4>
        <InfluenceTypeBadge type={asset.influence_type} />
      </div>
      <p className="text-xs text-slate-600 bg-white p-2 rounded-lg border border-slate-100">
        {asset.explanation}
      </p>
    </div>
  );
};
