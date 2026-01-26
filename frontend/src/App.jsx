import { useState, useEffect } from 'react'
import FighterCard from './FighterCard'
import FightSimulator from './FightSimulator'


import ThreeJsViewer from './ThreeJsViewer'
//import ThreeJsViewer from './ThreeJsTest'

import { fetchFighters, transformFighterData } from './api'
import './App.css'

function App() {
  const [availableFighters, setAvailableFighters] = useState([]);
  const [selectedFighters, setSelectedFighters] = useState({
    red: null,
    blue: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fightMode, setFightMode] = useState(false); // Toggle between selection and fight view

  // Fetch fighters when component mounts
  useEffect(() => {
    loadFighters();
  }, []);

  async function loadFighters() {
    try {
      setLoading(true);
      setError(null);
      
      const fightersData = await fetchFighters();
      console.log('Fetched fighters:', fightersData);
      
      // Transform the data to match our component expectations
      const transformed = fightersData.map(transformFighterData);
      setAvailableFighters(transformed);
      
      // Auto-select first two fighters if available
      if (transformed.length >= 2) {
        setSelectedFighters({
          red: transformed[0],
          blue: transformed[1]
        });
      } else if (transformed.length === 1) {
        setSelectedFighters({
          red: transformed[0],
          blue: null
        });
      }
      
    } catch (err) {
      console.error('Failed to load fighters:', err);
      setError('Failed to connect to Combat Protocol backend. Make sure the server is running on http://localhost:5001');
    } finally {
      setLoading(false);
    }
  }

  function handleFighterSelect(corner, fighterId) {
    const fighter = availableFighters.find(f => f.id === fighterId);
    setSelectedFighters(prev => ({
      ...prev,
      [corner]: fighter
    }));
  }

  function handleStartFight() {
    if (!selectedFighters.red || !selectedFighters.blue) {
      alert('Please select both fighters first!');
      return;
    }
    
    // Switch to fight mode
    setFightMode(true);
  }

  function handleFightEnd(result) {
    console.log('Fight ended:', result);
    // Stay in fight mode to show results
  }

  function handleBackToSelection() {
    setFightMode(false);
  }

  if (loading) {
    return (
      <div className="app">
        <header className="app-header">
          <h1>⚔️ COMBAT PROTOCOL</h1>
          <p className="subtitle">Loading fighters...</p>
        </header>
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <header className="app-header">
          <h1>⚔️ COMBAT PROTOCOL</h1>
          <p className="subtitle">Connection Error</p>
        </header>
        <div className="error-message">
          <p>{error}</p>
          <button onClick={loadFighters} className="retry-button">
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>⚔️ COMBAT PROTOCOL</h1>
        <p className="subtitle">Physics-Based Fighting Simulation</p>
      </header>

      {!fightMode ? (
        // SELECTION MODE
        <>
          {/* Fighter Selection Dropdowns */}
          <div className="fighter-selection">
            <div className="select-container red">
              <label htmlFor="red-fighter">Red Corner</label>
              <select 
                id="red-fighter"
                value={selectedFighters.red?.id || ''}
                onChange={(e) => handleFighterSelect('red', e.target.value)}
              >
                <option value="">Select Fighter...</option>
                {availableFighters.map(fighter => (
                  <option key={fighter.id} value={fighter.id}>
                    {fighter.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="select-container blue">
              <label htmlFor="blue-fighter">Blue Corner</label>
              <select 
                id="blue-fighter"
                value={selectedFighters.blue?.id || ''}
                onChange={(e) => handleFighterSelect('blue', e.target.value)}
              >
                <option value="">Select Fighter...</option>
                {availableFighters.map(fighter => (
                  <option key={fighter.id} value={fighter.id}>
                    {fighter.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* 3D VIEWER - NEW! */}
          <ThreeJsViewer 
            fighterA={selectedFighters.red} 
            fighterB={selectedFighters.blue}
          />

          {/* Fighter Cards Display */}
          <div className="arena">
            <FighterCard fighter={selectedFighters.red} corner="red" />
            
            <div className="vs-badge">
              <span className="vs-text">VS</span>
            </div>
            
            <FighterCard fighter={selectedFighters.blue} corner="blue" />
          </div>

          {/* Controls */}
          <div className="controls">
            <button 
              className="start-button"
              onClick={handleStartFight}
              disabled={!selectedFighters.red || !selectedFighters.blue}
            >
              Start Fight
            </button>
          </div>

          {/* Fighter Count */}
          <div className="fighter-count">
            {availableFighters.length} fighter{availableFighters.length !== 1 ? 's' : ''} loaded
          </div>
        </>
      ) : (
        // FIGHT MODE
        <>
          <button className="back-button" onClick={handleBackToSelection}>
            ← Back to Selection
          </button>
          
          <FightSimulator 
            fighterA={selectedFighters.red}
            fighterB={selectedFighters.blue}
            onFightEnd={handleFightEnd}
          />
        </>
      )}
    </div>
  )
}

export default App
