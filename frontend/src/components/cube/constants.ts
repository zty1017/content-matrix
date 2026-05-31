import type { CubeFaceId } from '../../types/api';

export const FACE_ROTATIONS: Record<CubeFaceId, [number, number, number]> = {
  primary_card: [0, 0, 0],                
  snapshot: [0, Math.PI, 0],              
  related_assets: [0, Math.PI / 2, 0],    
  evidence: [0, -Math.PI / 2, 0],         
  source: [Math.PI / 2, 0, 0],            
  inferences: [-Math.PI / 2, 0, 0]        
};

export const DEFAULT_VIEW_ANGLE: [number, number, number] = [Math.PI / 6, -Math.PI / 4, 0];

export const NORMAL_TO_FACE: Record<string, CubeFaceId> = {
  "0,0,1": "primary_card",
  "0,0,-1": "snapshot",
  "-1,0,0": "related_assets",
  "1,0,0": "evidence",
  "0,1,0": "source",
  "0,-1,0": "inferences"
};
