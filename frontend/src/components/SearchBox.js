import React, { useState } from 'react';
import './SearchBox.css';

const SearchBox = () => {
  const [activeTab, setActiveTab] = useState('flights');

  const renderForm = () => {
    switch (activeTab) {
      case 'flights':
        return (
          <div className="search-form">
            <input type="text" placeholder="Origen" />
            <input type="text" placeholder="Destino" />
            <input type="date" placeholder="Fecha de Salida" />
            <input type="date" placeholder="Fecha de Regreso" />
            <input type="number" placeholder="Pasajeros" min="1" />
            <button type="submit">Buscar Vuelos</button>
          </div>
        );
      case 'hotels':
        return (
          <div className="search-form">
            {/* Placeholder for hotels form */}
            <p>Buscador de hoteles en construcción.</p>
          </div>
        );
      case 'packages':
        return (
          <div className="search-form">
            {/* Placeholder for packages form */}
            <p>Buscador de paquetes en construcción.</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="search-box-container">
      <div className="tabs">
        <button
          className={activeTab === 'flights' ? 'active' : ''}
          onClick={() => setActiveTab('flights')}
        >
          Vuelos
        </button>
        <button
          className={activeTab === 'hotels' ? 'active' : ''}
          onClick={() => setActiveTab('hotels')}
        >
          Hoteles
        </button>
        <button
          className={activeTab === 'packages' ? 'active' : ''}
          onClick={() => setActiveTab('packages')}
        >
          Paquetes
        </button>
      </div>
      <div className="form-container">
        {renderForm()}
      </div>
    </div>
  );
};

export default SearchBox;
