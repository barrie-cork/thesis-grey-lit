# Thesis Grey - Django Implementation


wsl to project folder: /mnt/d/Python/Projects/thesis-grey-lit
VE: source venv/bin/activate

## Quick Start Guide

This repository contains the Django-based implementation of Thesis Grey, a specialised search application for clinical guideline development and grey literature discovery.

## Project Overview

Thesis Grey helps researchers:
- Create and execute systematic search strategies
- Process and review search results efficiently
- Generate PRISMA-compliant reports
- Manage literature review workflows

## Technology Stack

- **Backend**: Django 4.2 with Django REST Framework
- **Database**: PostgreSQL with Redis for caching
- **Background Tasks**: Celery with Redis broker
- **Frontend**: React 18 with Vite and TailwindCSS
- **API Integration**: Google Search via Serper

## Development Setup

### Prerequisites
- Python 3.8+ (3.11+ recommended)
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL (or use Docker)
- Redis (or use Docker)

### Quick Setup with Docker

```bash
# Clone the repository
git clone <repository-url>
cd thesis-django

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access the application
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Admin: http://localhost:8000/admin
```

### Local Development Setup

```bash
# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/development.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Start backend services
python manage.py runserver  # Terminal 1
celery -A thesis_grey worker -l info  # Terminal 2

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev  # Starts on http://localhost:3000
```

## Project Structure

```
thesis_grey/
├── apps/                   # Django applications
│   ├── authentication/    # User management
│   ├── search_sessions/   # Session management
│   ├── search_strategy/   # Query building
│   ├── serp_execution/    # Search execution
│   ├── results_manager/   # Result processing
│   ├── review_results/    # Review workflow
│   └── reporting/         # Reports and exports
├── frontend/              # React application
├── thesis_grey/           # Django project settings
├── api/                   # API configuration
├── requirements/          # Python dependencies
└── docker-compose.yml     # Development containers
```

## Key Features

### Phase 1 Implementation
- ✅ User authentication and session management
- ✅ Search strategy builder with PIC framework
- ✅ Automated search execution via Google API
- ✅ Result processing and deduplication
- ✅ Review workflow with tagging system
- ✅ PRISMA-compliant reporting
- ✅ CSV/JSON export functionality

### Planned Phase 2 Enhancements
- 🔄 Advanced collaboration features
- 🔄 Multi-engine search integration
- 🔄 Enhanced duplicate detection
- 🔄 Custom reporting templates
- 🔄 Reference manager integration

## API Documentation

### Authentication
```http
POST /api/v1/auth/login/
POST /api/v1/auth/register/
POST /api/v1/auth/token/refresh/
```

### Search Sessions
```http
GET    /api/v1/search-sessions/
POST   /api/v1/search-sessions/
GET    /api/v1/search-sessions/{id}/
PATCH  /api/v1/search-sessions/{id}/
DELETE /api/v1/search-sessions/{id}/
```

### Search Execution
```http
POST /api/v1/serp-execution/sessions/{id}/execute/
GET  /api/v1/serp-execution/sessions/{id}/status/
```

### Results and Review
```http
GET    /api/v1/results/{session_id}/
GET    /api/v1/review-tags/?session_id={id}
POST   /api/v1/review-tags/
POST   /api/v1/review-tags/{id}/assign_to_result/
```

### Reporting
```http
GET /api/v1/reporting/sessions/{id}/report/
GET /api/v1/reporting/sessions/{id}/export/?format=csv
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific app tests
pytest apps/search_sessions/tests/

# Run frontend tests
cd frontend && npm test
```

## Deployment

### Production Deployment

```bash
# Build and deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

# Or deploy to cloud platforms
# (Documentation for AWS, Azure, GCP deployment)
```

### Environment Variables

Required environment variables:
```env
SECRET_KEY=your-secret-key
DB_NAME=thesis_grey
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
SERPER_API_KEY=your-serper-api-key
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Guidelines

- Follow Django best practices and PEP 8
- Write tests for new features
- Update documentation for API changes
- Use type hints where appropriate
- Follow the existing code structure

## Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL is running
docker-compose ps
# Reset database
docker-compose down -v && docker-compose up -d
```

**Celery Tasks Not Running**
```bash
# Check Redis connection
redis-cli ping
# Restart Celery worker
celery -A thesis_grey worker -l info
```

**Frontend Build Issues**
```bash
# Clear node modules and reinstall
cd frontend && rm -rf node_modules package-lock.json
npm install
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `/docs`
- Review the FAQ section

## Changelog

### Version 1.0.0 (Phase 1)
- Initial Django implementation
- Core search and review functionality
- Basic reporting and export features

### Roadmap
- Version 1.1.0: Enhanced UI and performance improvements
- Version 2.0.0: Phase 2 features and collaboration tools
