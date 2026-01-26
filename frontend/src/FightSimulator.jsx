import { useState, useRef, useEffect } from 'react';
import './FightSimulator.css';

function FightSimulator({ fighterA, fighterB, onFightEnd }) {
  const [fightState, setFightState] = useState({
    round: 0,
    fighterA: { ...fighterA, health: 100, stamina: 100 },
    fighterB: { ...fighterB, health: 100, stamina: 100 },
    actionLog: [],
    isActive: false,
    winner: null,
    result: null
  });

  const eventSourceRef = useRef(null);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  function startFight() {
    console.log('startFight called!');
    console.log('Fighter A:', fighterA);
    console.log('Fighter B:', fighterB);
    
    if (!fighterA || !fighterB) {
      console.error('Missing fighters!', { fighterA, fighterB });
      setFightState(prev => ({
        ...prev,
        actionLog: [{
          type: 'error',
          message: 'Error: Fighters not properly loaded',
          timestamp: Date.now()
        }]
      }));
      return;
    }

    // Reset state
    setFightState({
      round: 0,
      fighterA: { ...fighterA, health: 100, stamina: 100 },
      fighterB: { ...fighterB, health: 100, stamina: 100 },
      actionLog: [{
        type: 'info',
        message: 'Connecting to fight server...',
        timestamp: Date.now()
      }],
      isActive: true,
      winner: null,
      result: null
    });

    // Start SSE connection - use the correct endpoint format
    const url = `http://localhost:5001/api/simulate/${fighterA.id}/${fighterB.id}`;
    console.log('Starting fight with URL:', url);
    
    const eventSource = new EventSource(url, {
      withCredentials: true // Include cookies for authentication
    });
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log('SSE connection opened successfully');
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Event received:', data);
      handleFightEvent(data);
    };

    eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      console.error('EventSource readyState:', eventSource.readyState);
      eventSource.close();
      setFightState(prev => ({
        ...prev,
        isActive: false,
        actionLog: [...prev.actionLog, { 
          type: 'error', 
          message: 'Connection lost. Make sure you are logged in to the backend at http://localhost:5001',
          timestamp: Date.now()
        }]
      }));
    };
  }

  function handleFightEvent(data) {
    console.log('Fight event:', data);
    
    // Debug: log the full event structure for strikes/clinches
    if (data.type === 'strike' || data.type === 'clinch' || data.type === 'knockdown') {
      console.log('Event details:', JSON.stringify(data.event, null, 2));
    }

    // Helper function to get fighter name from A/B identifier
    const getFighterName = (identifier) => {
      if (!identifier) return 'Fighter';
      if (identifier === 'A' || identifier === fighterA.name) return fighterA.name;
      if (identifier === 'B' || identifier === fighterB.name) return fighterB.name;
      return identifier;
    };

    setFightState(prev => {
      const newState = { ...prev };

      switch (data.type) {
        case 'setup':
          newState.actionLog.push({
            type: 'setup',
            message: `${data.fighter_a.name} vs ${data.fighter_b.name}`,
            timestamp: Date.now()
          });
          if (data.trash_talk) {
            // Trash talk comes as an object with fighter_a and fighter_b properties
            if (typeof data.trash_talk === 'object') {
              if (data.trash_talk.fighter_a) {
                newState.actionLog.push({
                  type: 'trash_talk',
                  message: `💬 ${data.trash_talk.fighter_a}`,
                  timestamp: Date.now()
                });
              }
              if (data.trash_talk.fighter_b) {
                newState.actionLog.push({
                  type: 'trash_talk',
                  message: `💬 ${data.trash_talk.fighter_b}`,
                  timestamp: Date.now()
                });
              }
            } else if (typeof data.trash_talk === 'string') {
              // Handle if it's just a string
              newState.actionLog.push({
                type: 'trash_talk',
                message: `💬 ${data.trash_talk}`,
                timestamp: Date.now()
              });
            }
          }
          break;

        case 'match_start':
          newState.actionLog.push({
            type: 'match_start',
            message: `🥊 FIGHT BEGINS: ${data.fighter_a_name} vs ${data.fighter_b_name}!`,
            timestamp: Date.now()
          });
          break;

        case 'round_start':
          newState.round = data.round;
          newState.actionLog.push({
            type: 'round_start',
            message: `🔔 ROUND ${data.round}`,
            timestamp: Date.now()
          });
          break;

        case 'frame':
          // Update fighter health and stamina from frame data
          if (data.fighter_a_health !== undefined) {
            newState.fighterA = {
              ...newState.fighterA,
              health: data.fighter_a_health,
              stamina: data.fighter_a_stamina || newState.fighterA.stamina
            };
          }
          if (data.fighter_b_health !== undefined) {
            newState.fighterB = {
              ...newState.fighterB,
              health: data.fighter_b_health,
              stamina: data.fighter_b_stamina || newState.fighterB.stamina
            };
          }
          
          // Add action log entry if there's a description
          if (data.description) {
            newState.actionLog.push({
              type: 'action',
              message: data.description,
              timestamp: Date.now()
            });
          }
          break;

        case 'strike':
          const strikeEvent = data.event;
          if (strikeEvent) {
            const attackerName = getFighterName(strikeEvent.attacker_name || strikeEvent.attacker);
            const targetName = getFighterName(strikeEvent.target_name || strikeEvent.target);
            const technique = strikeEvent.technique || 'strike';
            const targetZone = strikeEvent.target_zone || strikeEvent.body_part || 'body';
            const damage = strikeEvent.damage || 0;
            const isCritical = strikeEvent.is_critical || strikeEvent.critical || false;
            
            newState.actionLog.push({
              type: isCritical ? 'critical' : 'strike',
              message: `${attackerName} ${technique} to ${targetName}'s ${targetZone}! ${damage.toFixed(1)} damage${isCritical ? ' (CRITICAL!)' : ''}`,
              timestamp: Date.now()
            });
          }
          break;

        case 'clinch':
          const clinchEvent = data.event;
          if (clinchEvent) {
            const initiatorName = getFighterName(clinchEvent.initiator_name || clinchEvent.initiator);
            newState.actionLog.push({
              type: 'clinch',
              message: `${initiatorName} initiates clinch!`,
              timestamp: Date.now()
            });
          }
          break;

        case 'knockdown':
          const knockdownEvent = data.event;
          if (knockdownEvent) {
            const fighterName = getFighterName(knockdownEvent.fighter_name || knockdownEvent.fighter);
            newState.actionLog.push({
              type: 'knockdown',
              message: `💥 ${fighterName} is KNOCKED DOWN!`,
              timestamp: Date.now()
            });
          }
          break;

        case 'round_end':
          newState.actionLog.push({
            type: 'round_end',
            message: `⏱️ Round ${data.round} ends - Score: ${data.fighter_a_score} - ${data.fighter_b_score}`,
            timestamp: Date.now()
          });
          break;

        case 'fight_end':
          newState.isActive = false;
          newState.winner = {
            name: data.winner
          };
          newState.result = data.method;
          newState.actionLog.push({
            type: 'fight_end',
            message: `🏆 ${data.winner} wins by ${data.method}!`,
            timestamp: Date.now()
          });

          // Close SSE connection
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
          }

          // Notify parent component
          if (onFightEnd) {
            onFightEnd(data);
          }
          break;

        case 'keepalive':
          // Just keep the connection alive during breaks
          break;

        case 'complete':
          // Fight stream complete
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
          }
          break;

        case 'error':
          newState.isActive = false;
          newState.actionLog.push({
            type: 'error',
            message: `❌ Error: ${data.message}`,
            timestamp: Date.now()
          });
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
          }
          break;

        default:
          console.log('Unknown event type:', data.type);
      }

      return newState;
    });
  }

  function stopFight() {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setFightState(prev => ({
      ...prev,
      isActive: false
    }));
  }

  return (
    <div className="fight-simulator">
      {/* Round Counter */}
      {fightState.round > 0 && (
        <div className="round-display">
          <span className="round-label">ROUND</span>
          <span className="round-number">{fightState.round}</span>
        </div>
      )}

      {/* Fighter Stats - Live Updates */}
      <div className="live-stats">
        <FighterLiveStats 
          fighter={fightState.fighterA} 
          corner="red"
          isWinner={fightState.winner?.name === fighterA.name}
        />
        
        <div className="stats-divider">VS</div>
        
        <FighterLiveStats 
          fighter={fightState.fighterB} 
          corner="blue"
          isWinner={fightState.winner?.name === fighterB.name}
        />
      </div>

      {/* Action Log */}
      <div className="action-log-container">
        <h3>Fight Log</h3>
        <div className="action-log">
          {fightState.actionLog.length === 0 ? (
            <div className="log-placeholder">Waiting for fight to start...</div>
          ) : (
            fightState.actionLog.map((entry, index) => (
              <div key={index} className={`log-entry ${entry.type}`}>
                {entry.message}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Fight Controls */}
      <div className="fight-controls">
        {!fightState.isActive && !fightState.winner && (
          <button className="fight-btn start" onClick={startFight}>
            ▶️ Start Fight
          </button>
        )}
        
        {fightState.isActive && (
          <button className="fight-btn stop" onClick={stopFight}>
            ⏹️ Stop Fight
          </button>
        )}

        {fightState.winner && (
          <button className="fight-btn restart" onClick={startFight}>
            🔄 Fight Again
          </button>
        )}
      </div>

      {/* Winner Announcement */}
      {fightState.winner && (
        <div className="winner-announcement">
          <h2>🏆 {fightState.winner.name} WINS!</h2>
          <p className="result-method">{fightState.result}</p>
        </div>
      )}
    </div>
  );
}

function FighterLiveStats({ fighter, corner, isWinner }) {
  return (
    <div className={`live-fighter-stats ${corner} ${isWinner ? 'winner' : ''}`}>
      <h3>{fighter.name}</h3>
      
      <div className="stat-bars">
        <div className="stat-row">
          <span className="stat-label">Health</span>
          <div className="stat-bar">
            <div 
              className="stat-fill health"
              style={{ 
                width: `${Math.max(0, fighter.health)}%`,
                transition: 'width 0.5s ease'
              }}
            />
          </div>
          <span className="stat-value">{Math.round(fighter.health)}%</span>
        </div>

        <div className="stat-row">
          <span className="stat-label">Stamina</span>
          <div className="stat-bar">
            <div 
              className="stat-fill stamina"
              style={{ 
                width: `${Math.max(0, fighter.stamina)}%`,
                transition: 'width 0.5s ease'
              }}
            />
          </div>
          <span className="stat-value">{Math.round(fighter.stamina)}%</span>
        </div>
      </div>
    </div>
  );
}

export default FightSimulator;
