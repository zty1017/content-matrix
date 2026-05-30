import React from 'react';

interface Props {
  source: unknown;
  asset: unknown;
  task: unknown;
}

export const DebugJsonPanel: React.FC<Props> = ({ source, asset, task }) => {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-slate-900 text-green-400 p-4 font-mono text-xs overflow-y-auto max-h-[30vh] border-t-4 border-indigo-500 z-50">
      <h3 className="text-white font-bold mb-2">DEBUG JSON PANEL</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <h4 className="text-slate-400 mb-1">Source Resolution</h4>
          <pre className="bg-black p-2 rounded overflow-x-auto">
            {JSON.stringify(source, null, 2)}
          </pre>
        </div>
        <div>
          <h4 className="text-slate-400 mb-1">VideoContentAsset</h4>
          <pre className="bg-black p-2 rounded overflow-x-auto">
            {JSON.stringify(asset, null, 2)}
          </pre>
        </div>
        <div>
          <h4 className="text-slate-400 mb-1">ReconstructionTask</h4>
          <pre className="bg-black p-2 rounded overflow-x-auto">
            {JSON.stringify(task, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
};
