import React from 'react';
import { motion } from 'framer-motion';
import { useCabinetStore } from '../../store/useCabinetStore';

export const CabinetSidebar: React.FC = () => {
  const { cabinetState, setCabinetState, shelves, assets, searchQuery, setSearchQuery, filterMode, setFilterMode } = useCabinetStore();

  const isExpanded = cabinetState === 'half' || cabinetState === 'expanded';

  return (
    <motion.div
      initial={false}
      animate={{ width: isExpanded ? 320 : 64 }}
      className="absolute left-0 top-16 bottom-0 z-30 flex pointer-events-auto shadow-[4px_0_24px_rgba(0,0,0,0.02)]"
    >
      <div className="glass-panel border-l-0 rounded-r-2xl h-full w-full flex flex-col overflow-hidden relative border-y-0">
        
        <div 
          className="h-14 border-b border-white/50 flex items-center px-4 cursor-pointer hover:bg-white/30 transition-colors shrink-0"
          onClick={() => setCabinetState(isExpanded ? 'collapsed' : 'half')}
        >
          <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center text-blue-500 font-bold shrink-0">
            C
          </div>
          {isExpanded && (
            <span className="ml-3 font-semibold text-slate-700 whitespace-nowrap">
              资产陈列柜
            </span>
          )}
        </div>

        {isExpanded && (
          <div className="p-3 space-y-2 border-b border-white/40 shrink-0 bg-white/20">
            <input 
              type="text" 
              placeholder="搜索资产..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white/50 border border-white/60 rounded-lg px-3 py-1.5 text-sm outline-none placeholder:text-slate-400 focus:border-blue-300"
            />
            <div className="flex gap-2">
              {['all', 'formal', 'draft'].map(mode => (
                <button 
                  key={mode}
                  onClick={() => setFilterMode(mode)}
                  className={`text-xs px-2 py-1 rounded-md transition-colors ${filterMode === mode ? 'bg-blue-100 text-blue-600' : 'bg-white/40 text-slate-500 hover:bg-white/60'}`}
                >
                  {mode === 'all' ? '全部' : mode === 'formal' ? '已入柜' : '草稿'}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="flex-1 overflow-y-auto scrollbar-hide py-4 px-3 space-y-6">
          {isExpanded ? (
            shelves.map((shelf) => {
              // Apply basic filtering to shelf assets based on search query and filter mode
              const filteredAssetIds = shelf.assetIds.filter(id => {
                const asset = assets[id];
                if (!asset) return false;
                if (filterMode !== 'all' && asset.status !== filterMode) return false;
                if (searchQuery && !asset.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
                return true;
              });

              return (
                <div key={shelf.id} className="space-y-3">
                  <div className="text-xs font-bold text-slate-400 tracking-wider uppercase px-2">
                    {shelf.title} ({filteredAssetIds.length})
                  </div>
                  
                  {filteredAssetIds.length === 0 ? (
                    <div className="px-2 py-4 border border-dashed border-slate-300/50 rounded-xl text-center text-xs text-slate-400 bg-white/20">
                      暂无符合条件的资产
                    </div>
                  ) : (
                    <div className="grid gap-2">
                      {filteredAssetIds.map((id) => {
                        const asset = assets[id];
                        if (!asset) return null;
                        return (
                          <div key={asset.id} className="glass-button p-3 rounded-xl cursor-pointer group relative overflow-hidden">
                            <div className="absolute -bottom-4 -right-4 w-12 h-12 bg-blue-400/20 rounded-full blur-xl group-hover:bg-blue-400/40 transition-all"></div>
                            
                            <div className="text-sm font-semibold text-slate-700 truncate relative z-10">
                              {asset.title}
                            </div>
                            <div className="text-xs text-slate-500 truncate mt-1 relative z-10">
                              {asset.shortSummary}
                            </div>
                            <div className="flex gap-1 mt-2 relative z-10">
                              {asset.scenarioTags.slice(0, 2).map(tag => (
                                <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div className="flex flex-col items-center gap-4 pt-2">
              <div className="w-10 h-10 rounded-xl bg-white/50 border border-white flex items-center justify-center text-slate-400 hover:text-blue-500 hover:bg-white cursor-pointer transition-colors shadow-sm">
                柜
              </div>
              <div className="w-10 h-10 rounded-xl bg-white/50 border border-white flex items-center justify-center text-slate-400 hover:text-blue-500 hover:bg-white cursor-pointer transition-colors shadow-sm">
                史
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};
