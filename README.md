# Thesis Grey Literature - Django Implementation

## 🚨 **CRITICAL DEVELOPER ALERT**

### **🚀 NEW DEVELOPERS START HERE**
**📋 [DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)** - Complete step-by-step onboarding checklist

### ⚠️ **CUSTOM USER MODEL IN USE**
This project uses a **CUSTOM USER MODEL** (`accounts.User`) instead of Django's default `auth.User`.

**📚 REQUIRED READING BEFORE DEVELOPMENT:**
- **[CUSTOM_USER_ALERT.md](CUSTOM_USER_ALERT.md)** - Critical implementation details
- **[DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)** - Complete setup checklist
- **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - Comprehensive development standards
- **[apps/accounts/README.md](apps/accounts/README.md)** - Custom User model documentation

**✅ Quick Reference:**
```python
# ✅ CORRECT - Always use this pattern
from django.contrib.auth import get_user_model
User = get_user_model()

# ❌ WRONG - Never use this (will break)
from django.contrib.auth.models import User
```

**⚠️ Failing to use the correct User model will cause database errors!**

---

## Quick Start Guide

This repository contains the Django-based implementation of a grey literature search and review application for systematic research and clinical guideline development.

## Project Overview

This Django application helps researchers:
- Create and manage literature review sessions
- Execute systematic search strategies
- Process and review search results efficiently
- Track workflow progress and collaboration
- Generate comprehensive reports

## Technology Stack

- **Backend**: Django 4.2
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Django templates with modern CSS/JS
- **Authentication**: Custom User model with UUID primary keys
- **Testing**: Django's built-in testing framework

## Development Setup

### Prerequisites
- Python 3.12+ 
- Git for version control
- Virtual environment (venv or virtualenv)

### Quick Setup

```bash
# Clone the repository
git clone <repository-url>
cd /mnt/d/Python/Projects/thesis-grey-lit

# Create and activate virtual environment
python -m venv venv



# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Access the application at http://localhost:8000
```

## Project Structure

```
thesis-grey-lit/
├── apps/                       # Django applications
│   ├── accounts/              # Custom User model and authentication
│   ├── review_manager/        # Core session management (working example)
│   ├── search_strategy/       # Search strategy building (future)
│   ├── serp_execution/        # Search execution (future)
│   ├── results_manager/       # Result processing (future)
│   ├── review_results/        # Review workflow (future)
│   └── reporting/             # Reports and exports (future)
├── templates/                  # HTML templates
├── static/                     # Static files (CSS, JS, images)
├── thesis_grey_project/       # Django project settings
├── docs/                      # Project documentation
├── venv/                      # Virtual environment (local)
├── requirements.txt           # Python dependencies
├── manage.py                  # Django management script
└── README.md                  # This file
```

## Key Features

### ✅ Implemented (Phase 1)
- **User Management**: Custom User model with UUID primary keys
- **Session Management**: Create, edit, delete, and duplicate literature review sessions
- **Workflow States**: Draft → Strategy Ready → Executing → Processing → Review → Completed → Archived
- **Activity Logging**: Complete audit trail of all session activities
- **Status History**: Detailed tracking of status changes and transitions
- **User Statistics**: Productivity metrics and completion rates
- **Access Control**: Users can only access their own sessions
- **Responsive UI**: Modern dashboard with search and filtering

### 🔄 Planned (Future Phases)
- Search strategy builder with PIC framework
- Automated search execution
- Result processing and deduplication
- Review workflow with tagging
- PRISMA-compliant reporting
- Advanced collaboration features

## Current Implementation

The **Review Manager** app (`apps/review_manager/`) serves as the working example and foundation for all other apps. It demonstrates:

- Proper custom User model usage
- Django model relationships and constraints
- Status workflow management
- Activity logging with signals
- Template-based UI with modern styling
- Comprehensive test coverage
- Management commands for sample data

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.review_manager

# Run with coverage (if installed)
coverage run --source='.' manage.py test
coverage report
```

## Development Workflow

1. **Read the onboarding documentation** (see links above)
2. **Understand the custom User model** (critical!)
3. **Examine the review_manager app** as your implementation reference
4. **Follow the established patterns** for new apps
5. **Write tests** using the custom User model
6. **Update documentation** as you add features

## Management Commands

```bash
# Create sample session data for testing
python manage.py create_sample_sessions --count 10

# Clean up test data
python manage.py create_sample_sessions --clean

# Check for common issues
python manage.py check
```

## URLs

- **Dashboard**: http://localhost:8000/review/
- **Admin**: http://localhost:8000/admin/
- **Session Detail**: http://localhost:8000/review/{session-id}/
- **Session Timeline**: http://localhost:8000/review/{session-id}/timeline/
- **Session History**: http://localhost:8000/review/{session-id}/history/

## Environment Variables

Required environment variables in `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
# Add other settings as needed
```

## Common Issues & Solutions

### **Error: "Manager isn't available; 'auth.User' has been swapped"**
**Solution**: You're using the wrong User model. Use `get_user_model()` instead.

### **Error: "Cannot assign User instance"**
**Solution**: Use `settings.AUTH_USER_MODEL` in model ForeignKeys.

### **Tests failing with User model errors**
**Solution**: Check your test setup uses `get_user_model()`.

See [CUSTOM_USER_ALERT.md](CUSTOM_USER_ALERT.md) for detailed solutions.

## Documentation

- **[DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)** - Complete setup checklist
- **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - Comprehensive development standards
- **[CUSTOM_USER_ALERT.md](CUSTOM_USER_ALERT.md)** - Critical User model information
- **[TEAM_LEAD_CHECKLIST.md](TEAM_LEAD_CHECKLIST.md)** - Project management tools
- **[docs/PRD.md](docs/PRD.md)** - Product requirements and architecture
- **[apps/review_manager/README.md](apps/review_manager/README.md)** - Working implementation example

## Contributing

1. **Read all onboarding documentation first**
2. **Understand the custom User model requirements**
3. **Follow the review_manager app patterns**
4. **Write comprehensive tests**
5. **Update documentation**
6. **Submit clean pull requests**

## Project Architecture

This is a Django 4.2 application built with:
- **Custom User Model**: UUIDs instead of integer primary keys
- **App-based Architecture**: Modular design with clear separation of concerns
- **Signal-based Activity Logging**: Automatic audit trail
- **Template-based Frontend**: Server-side rendering with modern styling
- **Comprehensive Testing**: Full test coverage with proper patterns

## Development Status

- **Phase 1**: ✅ Complete - Core session management with custom User model
- **Phase 2**: 🔄 In Progress - Search strategy and execution
- **Phase 3**: 📋 Planned - Review workflow and reporting
- **Phase 4**: 📋 Planned - Advanced features and collaboration

## License

This project is for academic/research use. See LICENSE file for details.

## Support

For development support:
1. Check the comprehensive documentation
2. Review the working review_manager app
3. Examine the test files for examples
4. Create issues for bugs or questions

---

**🎯 Goal**: Build a robust literature review platform that follows Django best practices and provides researchers with powerful tools for systematic review work.
