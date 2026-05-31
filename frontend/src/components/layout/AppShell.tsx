import React from 'react';
import { useAppStore } from '../../store/useAppStore';
import { useDemoInit } from '../../hooks/useDemoInit';
import { TopNav } from './TopNav';
import { BottomInputBar } from './BottomInputBar';
import { NarrativeStatusBar } from './NarrativeStatusBar';
import { CubeScene } from '../cube/CubeScene';
import { CabinetSidebar } from '../cabinet/CabinetSidebar';
import { RightPanel } from '../panels/RightPanel';
import { WorkshopView } from '../workshop/WorkshopView';

export const AppShell: React.FC = () => {
  const { currentMode } = useAppStore();
  
  useDemoInit();

  return (
    <div className="relative w-screen h-screen overflow-hidden">
      <TopNav />
      
      {(currentMode === 'current' || currentMode === 'cabinet') && (
        <>
          <NarrativeStatusBar />
          <CabinetSidebar />
          <CubeScene />
          <RightPanel />
          <BottomInputBar />
        </>
      )}

      {currentMode === 'workshop' && (
        <WorkshopView />
      )}
    </div>
  );
};
