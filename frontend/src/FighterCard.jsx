import React from 'react';
import './FighterCard.css';

function FighterCard({ fighter, corner }) {
  if (!fighter) {
    return (
      <div className={`fighter-card ${corner}`}>
        <div className="fighter-placeholder">
          <p>Select a fighter</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`fighter-card ${corner}`}>
      <div className="fighter-header">
        <h2>{fighter.name}</h2>
        <div className="fighter-nickname">"{fighter.nickname}"</div>
      </div>
      
      <div className="fighter-stats">
        <div className="stat-row">
          <span className="stat-label">Health:</span>
          <div className="stat-bar">
            <div 
              className="stat-fill health"
              style={{ width: `${(fighter.health / fighter.max_health) * 100}%` }}
            />
          </div>
          <span className="stat-value">{fighter.health}/{fighter.max_health}</span>
        </div>
        
        <div className="stat-row">
          <span className="stat-label">Stamina:</span>
          <div className="stat-bar">
            <div 
              className="stat-fill stamina"
              style={{ width: `${(fighter.stamina / fighter.max_stamina) * 100}%` }}
            />
          </div>
          <span className="stat-value">{fighter.stamina}/{fighter.max_stamina}</span>
        </div>
      </div>

      <div className="fighter-details">
        <div className="detail-item">
          <span className="detail-label">Weight:</span>
          <span className="detail-value">{fighter.mass} kg</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Height:</span>
          <span className="detail-value">{fighter.height} cm</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Reach:</span>
          <span className="detail-value">{fighter.reach} cm</span>
        </div>
      </div>

      {fighter.trash_talk && (
        <div className="fighter-trash-talk">
          <span className="quote-mark">"</span>
          {fighter.trash_talk}
          <span className="quote-mark">"</span>
        </div>
      )}
    </div>
  );
}

export default FighterCard;
