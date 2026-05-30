import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { MainDemo } from './views/MainDemo';
import { AssetLibrary } from './views/AssetLibrary';

function App() {
  return (
    <BrowserRouter>
      <nav className="bg-white border-b border-slate-200 px-6 py-3 flex gap-4">
        <Link to="/" className="text-sm font-bold text-indigo-600 hover:text-indigo-800">主演示页</Link>
        <Link to="/library" className="text-sm font-bold text-indigo-600 hover:text-indigo-800">资产库</Link>
      </nav>
      <Routes>
        <Route path="/" element={<MainDemo />} />
        <Route path="/library" element={<AssetLibrary />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
