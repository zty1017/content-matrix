import React, { useState, useEffect } from 'react';
import { VideoCard } from '../components/VideoCard';
import { AICollectButton } from '../components/AICollectButton';
import { ProcessingTimeline } from '../components/ProcessingTimeline';
import { DemoUserSwitcher } from '../components/DemoUserSwitcher';
import { DecisionCard } from '../components/DecisionCard';
import { DebugJsonPanel } from '../components/DebugJsonPanel';
import { api } from '../api/api';
import { DemoContext, ReconstructionTaskData } from '../types';

export const MainDemo: React.FC = () => {
  const [contexts, setContexts] = useState<DemoContext[]>([]);
  const [selectedContext, setSelectedContext] = useState<string>('');
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [processStep, setProcessStep] = useState(0);
  
  const [sourceData, setSourceData] = useState<unknown>(null);
  const [assetData, setAssetData] = useState<unknown>(null);
  const [taskData, setTaskData] = useState<ReconstructionTaskData | null>(null);
  
  const [showDebug, setShowDebug] = useState(false);

  // Load demo contexts on mount
  useEffect(() => {
    api.getDemoContexts().then(res => {
      // res could be a list or an object depending on the backend structure.
      // Assuming res is an array or res.contexts is an array
      const ctxList = Array.isArray(res) ? res : res.contexts || [];
      if (ctxList && ctxList.length > 0) {
        setContexts(ctxList);
        setSelectedContext(ctxList[0].context_id);
      } else {
        // Fallback to hardcoded mock contexts if API fails or returns empty
        const fallback = [
          { context_id: 'low_budget', name: '低预算用户', description: '', task_id: 'task_demo_douyin_08_food_low_budget' },
          { context_id: 'efficiency', name: '效率优先用户', description: '', task_id: 'task_demo_douyin_08_food_efficiency' },
          { context_id: 'culture', name: '本地文化用户', description: '', task_id: 'task_demo_douyin_08_food_culture' }
        ];
        setContexts(fallback);
        setSelectedContext(fallback[0].context_id);
      }
    }).catch(e => {
      console.error(e);
      const fallback = [
        { context_id: 'low_budget', name: '低预算用户', description: '', task_id: 'task_demo_douyin_08_food_low_budget' },
        { context_id: 'efficiency', name: '效率优先用户', description: '', task_id: 'task_demo_douyin_08_food_efficiency' },
        { context_id: 'culture', name: '本地文化用户', description: '', task_id: 'task_demo_douyin_08_food_culture' }
      ];
      setContexts(fallback);
      setSelectedContext(fallback[0].context_id);
    });
  }, []);

  // Fetch task data when context changes
  useEffect(() => {
    const ctx = contexts.find(c => c.context_id === selectedContext);
    if (ctx && processStep >= 4) {
      api.getTask(ctx.task_id).then(res => {
        setTaskData(res);
      }).catch(e => console.error(e));
    }
  }, [selectedContext, contexts, processStep]);

  const handleCollect = async () => {
    setIsProcessing(true);
    setProcessStep(1);
    
    // Step 1: Resolve Source
    try {
      const source = await api.resolveSource('https://v.douyin.com/w3JLRkaZ6UQ/');
      setSourceData(source);
      await new Promise(r => setTimeout(r, 400));
      setProcessStep(2);
      
      // Step 2: Build Asset
      const resolvedId = source.resolved_source_id || 'w3JLRkaZ6UQ';
      const asset = await api.buildAsset(resolvedId);
      setAssetData(asset);
      await new Promise(r => setTimeout(r, 400));
      setProcessStep(3);
      
      // Step 3: Wait for Context & Card
      await new Promise(r => setTimeout(r, 400));
      setProcessStep(4);
      
      // The useEffect will trigger task fetching now.
    } catch {
      console.error('Mock fallback started');
      // If API fails, mock the process
      await new Promise(r => setTimeout(r, 500));
      setProcessStep(2);
      await new Promise(r => setTimeout(r, 500));
      setProcessStep(3);
      await new Promise(r => setTimeout(r, 500));
      setProcessStep(4);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSaveSnapshot = async () => {
    if (taskData?.task_id) {
      try {
        await api.saveSnapshot(taskData.task_id);
        alert('快照保存成功！');
      } catch {
        alert('Mock: 快照保存成功！');
      }
    }
  };

  const currentTask = taskData || {
    task_id: 'mock',
    primary_card: {
      common: { title: '暂无数据', summary: '点击左侧“AI 收藏”开始' },
      specific: { decision_level: '未知', one_sentence_judgement: '等待生成...', key_factors: [], needs_confirmation: [] }
    },
    related_assets: [],
    evidence_refs: [],
    action_entries: []
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-6 font-sans relative">
      <div className="max-w-7xl mx-auto flex flex-col h-full gap-6">
        <header className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
            Content Matrix - Web Demo
          </h1>
          <button onClick={() => setShowDebug(!showDebug)} className="text-sm px-3 py-1 bg-slate-200 rounded hover:bg-slate-300">
            {showDebug ? '隐藏调试面板' : '显示调试面板'}
          </button>
        </header>

        <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left Column: Video Card */}
          <div className="flex flex-col gap-4">
            <VideoCard />
            <AICollectButton onClick={handleCollect} disabled={isProcessing || processStep >= 4} />
          </div>

          {/* Middle Column: Processing & Context */}
          <div className="flex flex-col gap-6">
            <ProcessingTimeline step={processStep} />
            {processStep >= 4 && (
              <DemoUserSwitcher 
                contexts={contexts} 
                selectedContext={selectedContext} 
                onChange={setSelectedContext} 
              />
            )}
          </div>

          {/* Right Column: Decision Card */}
          <div className="flex flex-col gap-4">
            <DecisionCard data={currentTask} />
            {processStep >= 4 && (
              <button 
                onClick={handleSaveSnapshot}
                className="w-full py-2 bg-indigo-50 text-indigo-700 font-medium rounded-xl border border-indigo-200 hover:bg-indigo-100 transition-colors"
              >
                保存当前判断快照
              </button>
            )}
          </div>
        </div>
      </div>

      {showDebug && (
        <DebugJsonPanel source={sourceData} asset={assetData} task={taskData} />
      )}
    </div>
  );
};
