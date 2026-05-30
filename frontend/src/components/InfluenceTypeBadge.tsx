import React from 'react';

interface Props {
  type: 'supplement' | 'preference_adaptation' | 'conflict_warning' | string;
}

export const InfluenceTypeBadge: React.FC<Props> = ({ type }) => {
  const getBadgeStyle = () => {
    switch (type) {
      case 'preference_adaptation':
        return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'conflict_warning':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'supplement':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getLabel = () => {
    switch (type) {
      case 'preference_adaptation': return '偏好适配';
      case 'conflict_warning': return '冲突警告';
      case 'supplement': return '信息补充';
      default: return type;
    }
  };

  return (
    <span className={`text-xs px-2 py-1 rounded-md border font-medium ${getBadgeStyle()}`}>
      {getLabel()}
    </span>
  );
};
