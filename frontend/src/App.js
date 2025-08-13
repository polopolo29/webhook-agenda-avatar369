import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';

// En el futuro, aquí importaríamos otras páginas
// import SearchResultsPage from './pages/SearchResultsPage';
// import PackageDetailPage from './pages/PackageDetailPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
          {/* <Route path="/search" element={<SearchResultsPage />} /> */}
          {/* <Route path="/package/:id" element={<PackageDetailPage />} /> */}
        </Routes>
        {/* El Footer podría ir aquí */}
      </div>
    </Router>
  );
}

export default App;
