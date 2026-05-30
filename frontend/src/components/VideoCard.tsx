import React from 'react';

export const VideoCard: React.FC = () => {
  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-4">
      <div className="aspect-[9/16] bg-slate-800 rounded-xl relative overflow-hidden flex items-center justify-center">
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent z-10" />
        <span className="text-white z-20 font-medium tracking-wider opacity-80">视频封面 / 播放器</span>
        <div className="absolute bottom-4 left-4 right-4 z-20">
          <h3 className="text-white text-lg font-bold leading-tight">
            昨晚做了个饿梦，梦到我又去雾都了
          </h3>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {['重庆', '美食', '本地生活', '旅行', '全天吃喝路线'].map(tag => (
          <span key={tag} className="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded-md">
            #{tag}
          </span>
        ))}
      </div>
      <div className="text-xs text-slate-400 mt-2">
        <p>提示：本地 fixture 映射，不调用真实抖音 API</p>
      </div>
    </div>
  );
};
