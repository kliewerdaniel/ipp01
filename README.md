# Interview Prep Platform

A comprehensive platform for interview preparation with AI-powered feedback, voice recording, and transcription capabilities.

## Overview

This platform helps users prepare for interviews by:
- Practicing with AI-generated questions
- Recording and transcribing interview responses
- Receiving AI-powered feedback on responses
- Tracking progress through a personalized dashboard

## Tech Stack

### Frontend
- Next.js with TypeScript
- React Query for state management
- Tailwind CSS for styling
- Framer Motion for animations

### Backend
- FastAPI (Python)
- PostgreSQL database
- SQLAlchemy ORM
- Alembic for migrations

### Authentication
- JWT-based authentication
- OAuth integration (Google, GitHub)

### Payment Processing
- Stripe integration

### AI Services
- OpenAI integration for response feedback
- Voice recording and transcription

## Project Structure

```
interview-prep-platform/
├── frontend/                  # Next.js frontend application
│   ├── public/                # Static assets
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Next.js pages
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API service integration
│   │   ├── styles/            # Global styles
│   │   ├── types/             # TypeScript type definitions
│   │   ├── utils/             # Utility functions
│   │   └── context/           # React context providers
│   ├── tests/                 # Frontend tests
│   ├── next.config.js         # Next.js configuration
│   └── tsconfig.json          # TypeScript configuration
│
├── backend/                   # FastAPI backend application
│   ├── app/
│   │   ├── api/               # API routes and endpoints
│   │   ├── core/              # Core application components
│   │   ├── db/                # Database models and migrations
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic services
│   │   └── utils/             # Utility functions
│   ├── tests/                 # Backend tests
│   ├── alembic/               # Database migrations
│   └── requirements.txt       # Python dependencies
│
├── docker/                    # Docker configuration
│   ├── frontend/              # Frontend Docker configuration
│   ├── backend/               # Backend Docker configuration
│   └── docker-compose.yml     # Docker Compose configuration
│
└── docs/                      # Project documentation
    ├── architecture/          # Architecture diagrams
    ├── api/                   # API documentation
    └── deployment/            # Deployment instructions
```

## Setup Instructions

### Prerequisites
- Node.js (v16+)
- Python (v3.9+)
- PostgreSQL (v13+)
- Docker and Docker Compose (optional)

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Start development server
npm run dev
```

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Using Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Development Guidelines

- Follow the coding standards and best practices outlined in `ai_guidelines01.md`
- Submit pull requests with comprehensive descriptions
- Ensure all tests pass before merging

## License

MIT
