# Soda Trading Bot Setup Guide

## Prerequisites
- Git
- Docker and Docker Compose
- Node.js 18+ (for dashboard development)
- Python 3.10 (for backend development - required for Solana compatibility)

## Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/BenWarbie/Soda.git
cd Soda
```

2. Create environment configuration:
```bash
cp .env.example .env
```

3. Configure environment variables in `.env`:
```bash
# Required configurations detailed in .env.example
```

## Development Environment

### Using Docker (Recommended)
1. Start the services:
```bash
docker-compose up --build
```

2. Access the applications:
- Dashboard: http://localhost:3000
- API: http://localhost:8000

### Local Development

#### Backend (FastAPI)
1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the development server:
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (React + TypeScript)
1. Navigate to dashboard directory:
```bash
cd dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

## Application Components

### Backend
- FastAPI application (`src/api/`)
- WebSocket server for real-time updates
- Trading execution engine
- Analytics system

### Frontend
- React + TypeScript dashboard
- Real-time trading data visualization
- Configuration management interface
- Analytics dashboard

## Health Checks
Both services include health check endpoints:
- API: http://localhost:8000/health
- Dashboard: http://localhost:3000

Health check configuration:
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

## Troubleshooting

### Docker Issues
If encountering Docker storage driver issues:
1. Stop Docker service:
```bash
sudo systemctl stop docker
```

2. Update Docker daemon configuration:
```bash
sudo tee /etc/docker/daemon.json <<EOF
{
  "storage-driver": "vfs"
}
EOF
```

3. Restart Docker:
```bash
sudo systemctl start docker
```

### Python Dependencies
If encountering websockets compatibility issues:
1. Update the package: `pip install websockets==11.0.3`

### Common Issues
1. Port conflicts:
   - Ensure ports 3000 and 8000 are available
   - Check for other services using these ports

2. Environment variables:
   - Verify `.env` file exists
   - Check all required variables are set

3. Network issues:
   - Verify Solana RPC endpoint is accessible
   - Check WebSocket connection status

## Development Workflow
1. Create feature branch
2. Implement changes
3. Run linting:
   - Backend: `black src/`
   - Frontend: `npm run lint`
4. Submit pull request

## Deployment
1. Build images:
```bash
docker-compose build
```

2. Start services:
```bash
docker-compose up -d
```

3. Monitor logs:
```bash
docker-compose logs -f
```
