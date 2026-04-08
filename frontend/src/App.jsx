import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Register from './pages/Register'; 

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} /> {/* <-- 2. Ajoute cette route */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="*" element={<div style={{padding: '20px'}}><h2>404 - Page non trouvée</h2><a href="/">Retour au login</a></div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;