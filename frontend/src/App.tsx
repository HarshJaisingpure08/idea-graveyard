import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import IdeaDetail from './pages/IdeaDetail';
import Graveyard from './pages/Graveyard';
import Import from './pages/Import';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <div className="nav-inner">
          <NavLink to="/" className="nav-brand">Idea Graveyard</NavLink>
          <ul className="nav-links">
            <li>
              <NavLink to="/" end className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                Dashboard
              </NavLink>
            </li>
            <li>
              <NavLink to="/graveyard" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                Archive
              </NavLink>
            </li>
            <li>
              <NavLink to="/import" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                Import
              </NavLink>
            </li>
          </ul>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/idea/:id" element={<IdeaDetail />} />
        <Route path="/graveyard" element={<Graveyard />} />
        <Route path="/import" element={<Import />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
