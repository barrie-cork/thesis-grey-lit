# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## MCP Configuration

This project is configured with the following MCP servers for enhanced Claude Code functionality:

- **context7**: Upstash Context7 for enhanced context management
- **playwright**: Browser automation for testing and web scraping
- **perplexity-mcp**: Perplexity AI integration for enhanced search and reasoning

Configuration files are located at:
- `.claude/mcp_config.json` (primary)
- `claude_code_config.json` (alternative)

## Project Overview

**Thesis Grey Literature** is a Django 4.2 web application for systematic literature review and clinical guideline development. It helps researchers find, manage, and review "grey literature" following PRISMA standards.

## Critical Architecture Requirements

### ⚠️ Custom User Model (MANDATORY)
This project uses a **custom User model** (`accounts.User`) with UUID primary keys. This affects ALL development:

**ALWAYS use this pattern:**
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# In models:
created_by = models.ForeignKey(settings.AUTH_USER_MODEL, ...)
```

**NEVER use:**
```python
from django.contrib.auth.models import User  # Will break everything
```

### Reference Implementation
The `review_manager` app is the complete reference implementation demonstrating all patterns, testing approaches, and architectural decisions. Study this app before implementing new features.

## Essential Development Commands

### Setup and Environment
```bash
# Environment setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Database operations
python manage.py migrate
python manage.py createsuperuser

# Create test data
python manage.py create_sample_sessions --count 10 --username testuser
python manage.py create_sample_sessions --clean  # Remove test data
```

### Testing and Quality
```bash
# Run tests
python manage.py test
python manage.py test apps.review_manager
python manage.py test apps.accounts

# Security tests
python manage.py run_security_tests
python manage.py security_audit

# Development server
python manage.py runserver
```

## Architecture Overview

### App Structure (Feature-Based)
- **accounts**: Custom User model and authentication foundation (✅ COMPLETE)
- **review_manager**: Core session management (✅ COMPLETE - use as reference)
- **search_strategy**: PIC framework search definition (🔄 planned)
- **serp_execution**: API integration with background tasks (🔄 planned)
- **results_manager**: Results processing and deduplication (🔄 planned)
- **review_results**: Review workflow with tagging (🔄 planned)
- **reporting**: PRISMA-compliant reports (🔄 planned)

### Core Models (review_manager)
- **SearchSession**: Main entity with 9-state workflow (draft → strategy_ready → executing → processing → ready_for_review → in_review → completed → failed → archived)
- **SessionActivity**: Comprehensive audit trail with automatic signal-based logging
- **SessionStatusHistory**: Status transition tracking with timing and validation
- **SessionArchive**: Archive management with metadata
- **UserSessionStats**: User productivity metrics and analytics

### Technology Stack
- **Django 4.2** with split settings (base, local, production, test)
- **PostgreSQL** with psycopg 3 (production), SQLite (development)
- **Celery + Redis** for background tasks
- **UUID primary keys** throughout (via custom User model)
- **Signal-based activity logging** for audit trails

## Development Patterns

### Model Development
```python
# Always use get_user_model()
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class MyModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Use UUIDs for primary keys to match User model
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```

### Testing Patterns
```python
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class MyTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
```

### View Security Patterns
```python
# Use provided decorators from review_manager.decorators
from apps.review_manager.decorators import owns_session, session_status_required, rate_limit

@login_required
@owns_session
@session_status_required('draft', 'strategy_ready')
def my_view(request, session_id):
    # request.session_obj is available from @owns_session
    pass
```

## Business Logic

### Session Workflow States
1. **draft**: Initial creation, can be edited/deleted
2. **strategy_ready**: Search strategy defined, ready for execution
3. **executing**: Background search execution in progress
4. **processing**: Results being processed and deduplicated
5. **ready_for_review**: Results ready for manual review
6. **in_review**: Active review in progress
7. **completed**: Review finished, can be archived
8. **failed**: Error state, can be reset to previous state
9. **archived**: Long-term storage, hidden from active views

### Automatic Activity Logging
All model changes trigger activity logging via Django signals. Use `SignalUtils.set_change_context()` to provide additional context:

```python
from apps.review_manager.signals import SignalUtils

SignalUtils.set_change_context(
    session,
    user=request.user,
    reason='Manual status change'
)
session.status = 'completed'
session.save()
```

## Testing Requirements

### Security Testing
The project includes comprehensive security tests in `review_manager.tests_sprint8`. New features must include:
- Permission boundary tests
- Rate limiting validation
- CSRF protection verification
- Input validation tests
- Audit logging verification

### Test Data Generation
Use management commands for consistent test data:
```bash
python manage.py create_sample_sessions --count 10
```

## Database Considerations

### Migrations with Custom User
Always test migrations with the custom User model. Use proper UUID handling:
```python
# In migrations
import uuid
default=uuid.uuid4
```

### Query Optimization
Follow patterns from review_manager for performance:
- Use `select_related()` for ForeignKey relationships
- Use `prefetch_related()` for reverse relationships
- Add database indexes on frequently queried fields

## Security Implementation

### Permission System
- User-owned sessions with ownership validation
- Status-based access control
- Rate limiting on sensitive operations
- Comprehensive audit logging

### Required Security Decorators
- `@owns_session`: Validates session ownership
- `@session_status_required`: Validates status prerequisites
- `@rate_limit`: Prevents abuse of endpoints
- `@audit_action`: Logs security-relevant actions

## Documentation Standards

### Required Documentation
- App-level README.md with implementation details
- Model docstrings with field explanations
- View docstrings with permission requirements
- Test documentation with security scenarios

### Existing Documentation
- **DEVELOPER_ONBOARDING.md**: Complete setup guide
- **CUSTOM_USER_ALERT.md**: User model critical information
- **DEVELOPMENT_GUIDE.md**: Comprehensive development standards
- **docs/PRD.md**: Product requirements and architecture

## Common Development Tasks

### Adding a New App
1. Study `review_manager` app structure and patterns
2. Use `get_user_model()` throughout
3. Implement UUID primary keys for consistency
4. Add comprehensive tests including security scenarios
5. Follow the established URL and view patterns
6. Implement proper permission decorators

### Extending Session Functionality
1. Add new fields to `SearchSession` model
2. Update status workflow if needed
3. Add activity logging for new actions
4. Implement appropriate permissions
5. Add tests for new functionality
6. Update templates and views

### Background Task Implementation
```python
# Use Celery for long-running operations
from celery import shared_task

@shared_task
def process_search_results(session_id):
    session = SearchSession.objects.get(id=session_id)
    # Implementation
```

## Error Handling

### Custom User Model Errors
- **"Manager isn't available; 'auth.User' has been swapped"**: Use `get_user_model()`
- **"Cannot assign User instance"**: Use `settings.AUTH_USER_MODEL` in ForeignKeys
- **Test failures with User model**: Ensure tests use `get_user_model()`

### Status Workflow Errors
- **Invalid status transitions**: Check `SearchSession.Status` choices
- **Permission denied**: Verify user ownership and status requirements
- **Activity logging failures**: Ensure proper signal context setup

## Performance Considerations

### Database Optimization
- Use database indexes on UUID fields for joins
- Implement pagination for large datasets
- Use query optimization patterns from review_manager
- Consider caching for frequently accessed statistics

### Template Optimization
- Use template inheritance from `review_manager/base.html`
- Implement AJAX for dynamic updates
- Follow responsive design patterns

## Integration Points

### External APIs
- Celery task queue for background processing
- Redis for caching and message brokerage
- PostgreSQL for production database
- Future: Search APIs (Google, academic databases)

### Frontend Integration
- Django templates with modern CSS/JavaScript
- AJAX endpoints for dynamic functionality
- Bootstrap-based responsive design
- Future: REST API for mobile/SPA applications