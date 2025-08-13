import React from 'react';
import './FeaturedPackages.css';

// Datos de ejemplo. En el futuro, esto vendría de una API.
const packages = [
  {
    id: 1,
    title: 'Maravillas de China',
    description: '10 días explorando Beijing, Shanghai y la Gran Muralla.',
    price: 'Desde 45,000 MXN',
    imageUrl: 'https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?q=80&w=2070'
  },
  {
    id: 2,
    title: 'Safari en Kenia',
    description: 'Vive la emoción de la sabana africana y el Monte Kilimanjaro.',
    price: 'Desde 55,000 MXN',
    imageUrl: 'https://images.unsplash.com/photo-1534430480872-3498386e7856?q=80&w=1974'
  },
  {
    id: 3,
    title: 'Joyas de Europa del Este',
    description: 'Descubre la historia de Praga, Viena y Budapest.',
    price: 'Desde 40,000 MXN',
    imageUrl: 'https://images.unsplash.com/photo-1523952578875-e6de1c225848?q=80&w=2070'
  }
];

const FeaturedPackages = () => {
  return (
    <section className="featured-packages">
      <h2 className="section-title">Paquetes Destacados</h2>
      <div className="packages-container">
        {packages.map(pkg => (
          <div key={pkg.id} className="package-card">
            <img src={pkg.imageUrl} alt={pkg.title} className="package-image" />
            <div className="package-info">
              <h3>{pkg.title}</h3>
              <p>{pkg.description}</p>
              <span className="package-price">{pkg.price}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default FeaturedPackages;
