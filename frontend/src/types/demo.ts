import type { UiCubeModel } from "./cube";

export interface DemoScenario {
  id: string;
  title: string;
  subtitle: string;
  defaultContextId: string;
  heroCube: Partial<UiCubeModel>;
}
