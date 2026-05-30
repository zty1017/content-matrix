import React from 'react';

export const VideoCard: React.FC = () => {
  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-4">
      <div className="aspect-[9/16] bg-slate-800 rounded-xl relative overflow-hidden flex items-center justify-center group">
        <video 
          className="absolute inset-0 w-full h-full object-cover"
          poster="/assets/covers/08-美食-昨晚做了个饿梦-梦到我又去雾都了-cover.jpg"
          src="/assets/videos/08-美食-昨晚做了个饿梦-梦到我又去雾都了.mp4"
          controls
          controlsList="nodownload"
          playsInline
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent z-10 pointer-events-none" />
        <div className="absolute bottom-4 left-4 right-4 z-20 pointer-events-none">
          <h3 className="text-white text-lg font-bold leading-tight drop-shadow-md">
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
