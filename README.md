# Combat Protocol

A physics-based Muay Thai fighting simulation with AI-generated fighters and real-time 3D visualization.

## Project Structure

```
combat-protocol/
├── backend/          # Flask API server and physics simulation
├── frontend/         # React + Three.js web interface
├── docs/             # Documentation and git history
├── legal/            # Legal documents
├── papers/           # Research papers
└── scripts/          # Utility scripts
```

## Quick Start

### Backend (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend runs on `http://localhost:5001`

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173/v2/`

## Development

- **Local Development**: Both servers run independently
- **Production**: Frontend builds to static files served by Flask

## Documentation

See `docs/` for detailed system documentation and git history.

## Deployment

Production site: https://combatprotocol.com/v2/
