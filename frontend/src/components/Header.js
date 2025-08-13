import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header = () => {
  return (
    <header className="main-header">
      <div className="header-content">
        <div className="logo">
          <Link to="/">Viajes Web</Link>
        </div>
        <nav className="main-nav">
          <ul>
            <li><Link to="/vuelos">Vuelos</Link></li>
            <li><Link to="/hoteles">Hoteles</Link></li>
            <li><Link to="/paquetes">Paquetes</Link></li>
          </ul>
        </nav>
        <div className="header-actions">
          {/* Placeholder for language switcher and login */}
          <span>ES | FR</span>
          <button className="login-button">Login</button>
        </div>
      </div>
    </header>
  );
};

export default Header;
