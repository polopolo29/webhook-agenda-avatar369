import React from 'react';
import SearchBox from '../components/SearchBox';
import FeaturedPackages from '../components/FeaturedPackages';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="home-page">
      <div className="hero-section">
        <div className="hero-content">
          <h1>Tu Próxima Aventura Comienza Aquí</h1>
          <p>Explora destinos exóticos y reserva el viaje de tus sueños.</p>
        </div>
        <SearchBox />
      </div>
      <FeaturedPackages />
    </div>
  );
};

export default HomePage;
