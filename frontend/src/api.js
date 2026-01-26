// api.js - Combat Protocol API Service

// Use localhost for development, production domain otherwise
const isDevelopment = import.meta.env.DEV;
const API_BASE_URL = isDevelopment 
  ? 'http://localhost:5001'  // Local Flask backend
  : window.location.origin;   // Production: https://combatprotocol.com

console.log('API_BASE_URL:', API_BASE_URL, '(isDevelopment:', isDevelopment, ')');

/**
 * Fetch all available fighters from the backend
 */
export async function fetchFighters() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/fighters`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching fighters:', error);
    throw error;
  }
}

/**
 * Fetch detailed info about a specific fighter
 */
export async function fetchFighterDetails(fighterId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/fighter/${fighterId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Error fetching fighter ${fighterId}:`, error);
    throw error;
  }
}

/**
 * Fetch available 3D models
 */
export async function fetchModels() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching models:', error);
    throw error;
  }
}

/**
 * Transform backend fighter data to match our FighterCard component expectations
 */
export function transformFighterData(backendFighter) {
  return {
    id: backendFighter.id,
    name: backendFighter.name,
    nickname: backendFighter.nickname || backendFighter.discipline || "The Fighter",
    health: 100, // Start at full health
    max_health: 100,
    stamina: 100, // Start at full stamina  
    max_stamina: 100,
    mass: backendFighter.physical?.weight_kg || 75,
    height: backendFighter.physical?.height_cm || 175,
    reach: backendFighter.physical?.reach_cm || 180,
    trash_talk: backendFighter.trash_talk || null,
    image_url: backendFighter.image_url || null,
    stats: backendFighter.stats || {}
  };
}
