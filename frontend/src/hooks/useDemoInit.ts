import { useEffect } from 'react';
import { useCubeStore } from '../store/useCubeStore';
import { useAppStore } from '../store/useAppStore';
import { demoScenarios } from '../data/demoScenarios';
import type { UiCubeModel } from '../types/cube';

export const useDemoInit = () => {
  const { setCurrentCubeView } = useCubeStore();
  const { currentDemoContext } = useAppStore();

  useEffect(() => {
    const scenario = demoScenarios.find(s => s.id === currentDemoContext) || demoScenarios[0];
    if (scenario && scenario.heroCube) {
      setCurrentCubeView(scenario.heroCube as UiCubeModel);
    }
  }, [currentDemoContext, setCurrentCubeView]);
};
