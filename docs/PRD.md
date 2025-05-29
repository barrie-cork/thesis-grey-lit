# Thesis Grey: Master Project Plan (Django Edition)

**Project Title:** Thesis Grey
**Version:** 2.0
**Date:** 2025-05-29
**Phase:** 1

## 1. Executive Summary

Thesis Grey is a specialized web application designed to help researchers, particularly those developing clinical guidelines, systematically find, manage, and review "grey literature" – research found outside traditional academic databases (like reports, theses, conference proceedings). It streamlines the process of creating search strategies, running them against search engines like Google, and organizing the results for review, following best practices like PRISMA.

The application, built using the **Django 4.2 framework**, addresses the challenge of finding relevant grey literature for systematic reviews and clinical guidelines, which is currently a manual, time-consuming, and often unsystematic process. Researchers struggle to document their search strategies, efficiently execute searches across multiple sources, manage large volumes of results, and track the review process in a way that meets reporting standards like PRISMA.

### Key Benefits

- **Saves significant researcher time** by automating search execution and results organization.
- **Improves the rigor and comprehensiveness** of literature reviews by making grey literature searching more systematic.
- **Organizes information** effectively, managing search strategies, results, and review decisions in one place.
- **Supports compliance** with reporting standards like PRISMA through structured workflows and data export.

## 2. Project Goals (Phase 1)

1. Provide researchers with tools to create and execute systematic search strategies.
2. Enable efficient processing and review of search results.
3. Support PRISMA-compliant workflows for literature reviews.
4. Establish a foundation that can be extended in Phase 2 without significant refactoring.

## 3. Technical Architecture

### 3.1 Technology Stack

- **Framework:** Django `4.2.x` (Python)
- **Frontend:** Django Templates, HTML, CSS (with TailwindCSS), JavaScript (for AJAX interactivity)
- **Backend:** Django, Django ORM
- **Database:** PostgreSQL (using Psycopg 3)
- **APIs:** Google Search API via Serper (using a Python client like `requests`)
- **Background Tasks:** Celery with Redis as the message broker
- **DevOps:** Docker, GitHub Actions (basic CI/CD)
- **API Development (Phase 1):** Django built-in JSON responses for AJAX functionality, Django REST Framework for Phase 2 if needed

### 3.2 Architectural Approach

The project will adopt a **modular design using Django Apps**. Each core feature or domain will be encapsulated within its own app, promoting separation of concerns and maintainability. While Django's app structure provides a natural way to organize by feature, the principles of **Vertical Slice Architecture** will still guide development, focusing on implementing features end-to-end. This allows implementation to focus on one feature at a time, ensuring the feature in focus passes all tests before moving to the next. This should guide the roadmap.

**Each Django app should have its own detailed PRD** located in `docs/features/{app_name}/{app_name}-prd.md` that provides implementation-specific details while referencing this master PRD for overall context and architectural decisions.

### 3.3 Project Structure (Illustrative)

```
thesis_grey_project/
├── manage.py                 # Django's command-line utility
├── thesis_grey_project/      # Main project Python package
│   ├── __init__.py
│   ├── settings/             # Settings directory
│   │   ├── __init__.py
│   │   ├── base.py           # Base settings
│   │   ├── local.py          # Local development settings
│   │   └── production.py     # Production settings
│   ├── urls.py               # Project-level URL configuration
│   ├── wsgi.py               # WSGI entry-point
│   └── asgi.py               # ASGI entry-point (for Celery/Channels if needed)
├── apps/                     # Directory for all Django apps
│   ├── accounts/             # User authentication and profiles
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── templates/
│   │       └── accounts/
│   ├── review_manager/       # Review Manager Dashboard and session creation
│   │   └── ... (similar structure to accounts)
│   ├── search_strategy/      # Search Strategy definition
│   │   └── ...
│   ├── serp_execution/       # Search Execution and background tasks (Celery tasks)
│   │   ├── tasks.py          # Celery tasks
│   │   └── ...
│   ├── results_manager/      # Results processing and management
│   │   └── ...
│   ├── review_results/       # Results review, tagging, notes
│   │   └── ...
│   ├── reporting/            # Reporting and data export
│   │   └── ...
├── docs/                     # Documentation
│   ├── PRD.md                # This master PRD
│   └── features/             # App-specific PRDs
│       ├── review_manager/
│       │   └── review-manager-prd.md
│       ├── search_strategy/
│       │   └── search-strategy-prd.md
│       └── ...
├── static/                   # Project-wide static files (CSS, JS, images)
│   └── css/
│   └── js/
├── templates/                # Project-wide base templates
│   └── base.html
└── requirements/
    ├── base.txt
    ├── local.txt
    └── production.txt
```

### Directory Structure (within each app)

Each Django app (e.g., `apps/search_strategy/`) will generally follow this structure:

```
apps/{feature_app_name}/
├── __init__.py
├── admin.py         # Django admin configurations
├── apps.py          # App configuration
├── forms.py         # Django forms
├── migrations/      # Database migrations
├── models.py        # Django ORM models
├── templates/       # HTML templates specific to this app
│   └── {feature_app_name}/
│       ├── some_page.html
├── templatetags/    # Custom template tags and filters
├── tests.py         # Unit and integration tests
├── urls.py          # URL routing for this app
├── views.py         # View functions or class-based views
└── utils.py         # Utility functions specific to this app (if any)
```

### File types
- All Python code will be `.py`.
- HTML templates will be `.html`.
- Static assets will be `.css`, `.js`, etc.

### 3.4 Database Architecture

Phase 1 implements the full database schema designed for both phases, using the **Django ORM** with PostgreSQL. The core entities include:

#### Core Models

**SearchSession Model (Primary Entity)**
```python
class SearchSession(models.Model):
    # Core Phase 1 fields
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Search strategy fields (PIC framework)
    population_terms = models.JSONField(default=list, blank=True)
    interest_terms = models.JSONField(default=list, blank=True)
    context_terms = models.JSONField(default=list, blank=True)
    
    # Ownership and permissions
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sessions')
    
    # Phase 2 collaboration fields (prepared but unused in Phase 1)
    team = models.ForeignKey('teams.Team', null=True, blank=True, on_delete=models.SET_NULL)
    collaborators = models.ManyToManyField(User, blank=True, related_name='collaborative_sessions')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    permissions = models.JSONField(default=dict, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_sessions')
```

**Status Workflow**
```python
STATUS_CHOICES = [
    ('draft', 'Draft'),                    # Just created, no strategy defined
    ('strategy_ready', 'Strategy Ready'),  # PIC terms defined, ready to execute
    ('executing', 'Executing Searches'),   # Background tasks running
    ('processing', 'Processing Results'),  # Raw results being processed
    ('ready_for_review', 'Ready for Review'), # Results available for screening
    ('in_review', 'Under Review'),         # User actively reviewing results
    ('completed', 'Completed'),            # Review finished, ready for export
    ('failed', 'Failed'),                  # Error occurred during execution
    ('archived', 'Archived'),              # User archived completed session
]

VISIBILITY_CHOICES = [
    ('private', 'Private'),
    ('team', 'Team'),
    ('public', 'Public')
]
```

**Additional Core Models:**
- `User`: Stores user authentication and profile information (likely extending Django's built-in `AbstractUser`). `db_comment` will be used for clarity.
- `SearchQuery`: Defines specific queries within a session.
- `SearchExecution`: Tracks the execution of search queries.
- `RawSearchResult`: Stores raw data from search engines.
- `ProcessedResult`: Contains normalized and processed search results.
- `DuplicateRelationship`: Tracks duplicate results.
- `ReviewTag`: Defines tags for categorizing results (Include, Exclude, Maybe).
- `ReviewTagAssignment`: Links tags to results.
- `Note`: Stores notes added to results.
- `SessionActivity`: Audit trail for session changes and activities.

**Database Integrity Rules:**
- `created_by` uses `CASCADE` - when user is deleted, their sessions are deleted
- Audit fields (`performed_by`, `updated_by`) use `PROTECT` - preserves audit trail integrity
- Foreign keys to optional Phase 2 models use `SET_NULL` - allows graceful degradation

Django's migration system will manage schema changes.

## 4. Core Features

### 4.1 Authentication

**Description:** Basic user authentication system allowing researchers to register, log in, and manage their profiles.

**Key Components (Django context):**
- Django's built-in `AuthenticationForm`, `UserCreationForm`.
- Custom templates for login, signup, profile pages.
- Views: `LoginView`, `LogoutView`, custom views for signup and profile.

**Technical Implementation:**
- Utilizes Django's built-in authentication system (`django.contrib.auth`).
- Password hashing handled by Django.
- Session management handled by Django.
- Basic role-based permissions using Django's permission system or custom groups.
- Potentially a custom User model inheriting from `AbstractUser` if additional fields are needed.

### 4.2 Review Manager Dashboard

**Description:** Central landing page displaying the user's review sessions with smart navigation and comprehensive session management.

**Key Components (Django context):**
- `DashboardView` (Class-Based View) with session filtering and statistics
- `SessionCreateView` implementing two-step creation workflow
- `SessionDetailView`, `SessionUpdateView`, `SessionDeleteView` for full CRUD operations
- Django templates with responsive card-based layout
- Session duplication and archiving functionality

**Technical Implementation:**
- **Two-Step Session Creation:** Minimal creation (title + description) → immediate redirect to search strategy definition
- **Smart Navigation:** Session clicks route to next logical step based on status (draft → strategy, ready_for_review → results, etc.)
- **Status-Based Grouping:** Sessions organised by Active, Completed, Failed with visual status indicators
- **9-State Status Workflow:** Robust status management with transition validation
- **Session Management:** Delete (draft only), duplicate (any status), archive (completed only)
- **Future-Proof Design:** Collaboration fields built into SearchSession model for Phase 2 (unused in Phase 1)
- **Performance Optimised:** Database indexes and query optimisation for dashboard performance

**Status Workflow Management:**
```python
class SessionStatusManager:
    ALLOWED_TRANSITIONS = {
        'draft': ['strategy_ready'],
        'strategy_ready': ['executing', 'draft'],
        'executing': ['processing', 'failed'],
        'processing': ['ready_for_review', 'failed'],
        'ready_for_review': ['in_review'],
        'in_review': ['completed', 'ready_for_review'],
        'completed': ['archived', 'in_review'],
        'failed': ['draft', 'strategy_ready'],
        'archived': ['completed']
    }
```

**Detailed implementation specifications available in:** `docs/features/review_manager/review-manager-prd.md`

### 4.3 Search Strategy

**Description:** Interface for defining search strategies using the PIC framework (Population, Interest, Context) and configuring search parameters.

**Key Components (Django context):**
- `SearchStrategyView` (CBV or function view).
- Django `ModelForm` for `SearchSession` strategy fields.
- Django template for strategy definition.
- JavaScript for real-time query preview generation (if needed).
- ORM queries to fetch/update `SearchSession` data.
- A Celery task will be triggered to initiate searches.

**Technical Implementation:**
- Strategy saved to database via Django ORM.
- Execution triggers a Celery background job for API calls.

**Detailed implementation specifications available in:** `docs/features/search_strategy/search-strategy-prd.md` (to be created)

### 4.4 SERP Execution

**Description:** System for executing search queries against external APIs and tracking progress.

**Key Components (Django context):**
- `SearchExecutionStatusView` (CBV or function view) to show progress.
- Celery task (`perform_serp_query_task`) for making API calls to Serper using Python's `requests` library.
- Django ORM models to store `SearchExecution` status and `RawSearchResult`.
- JavaScript on the status page to periodically poll for updates (or WebSockets if more real-time updates are desired in a later iteration).

**Technical Implementation:**
- Integration with Serper API for Google Search.
- Background job queue using Celery with Redis/RabbitMQ.
- Progress tracking and error handling within the Celery task and Django models.
- Transition to Results Overview after completion.

**Detailed implementation specifications available in:** `docs/features/serp_execution/serp-execution-prd.md` (to be created)

### 4.5 Results Manager

**Description:** Backend system for processing raw search results and preparing them for review.

**Key Components (Django context):**
- Celery task or Django management command (`process_session_results_task`) for backend processing.
- Django ORM queries to fetch `RawSearchResult` and create/update `ProcessedResult`.
- `ResultsOverviewView` (CBV or function view) for displaying processed results.

**Technical Implementation:**
- URL normalization and basic metadata extraction using Python libraries.
- Basic deduplication based on normalized URLs using Django ORM.
- Filtering and sorting capabilities provided by Django ORM and views.

**Detailed implementation specifications available in:** `docs/features/results_manager/results-manager-prd.md` (to be created)

### 4.6 Review Results

**Description:** Interface for reviewing search results, applying tags, and adding notes, all within a single paginated view.

**Key Components (Django context):**
- `ResultsOverviewView` (CBV or function view) with pagination.
- Django templates for displaying results.
- Django Forms for tagging and adding notes.
- Django ORM queries for fetching `ProcessedResult` with pagination, `ReviewTag`, `Note`.
- Views/logic to handle `ReviewTagAssignment` and `Note` creation/updates.

**Technical Implementation:**
- Paginated results display using Django's Paginator.
- Mandatory tagging system (Include, Exclude, Maybe) via Django Forms and views - users must select one tag for each result to complete the review.
- Exclusion reason capture required when tagging as "Exclude".
- No reason required for Include or Maybe tags.
- Simple notes system integrated directly within the results view.
- PRISMA-compliant workflow.

**Detailed implementation specifications available in:** `docs/features/review_results/review-results-prd.md` (to be created)

### 4.7 Reporting

**Description:** System for generating reports and exporting data from review sessions.

**Key Components (Django context):**
- `ReportingView` (CBV or function view).
- Django templates for displaying statistics.
- Django ORM queries to aggregate report data.
- Python libraries for CSV (e.g., `csv` module), JSON (e.g., `json` module), and PDF (e.g., `ReportLab` or `WeasyPrint`) export.

**Technical Implementation:**
- Basic PRISMA flow statistics calculated via ORM queries.
- Search strategy summary display.
- CSV, JSON, and PDF export of included/excluded results.
- Summary statistics dashboard with tag distribution and domain distribution.

**Detailed implementation specifications available in:** `docs/features/reporting/reporting-prd.md` (to be created)

## 5. Project-Wide Standards

### 5.1 User Experience Standards

**Performance Requirements:**
- Dashboard loads in < 2 seconds with 100+ sessions
- Session search returns results in < 500ms
- Session creation completes in < 30 seconds
- All user actions receive immediate feedback

**Accessibility Standards:**
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- Minimum colour contrast 4.5:1
- Touch-friendly interface (44px minimum touch targets)

**Responsive Design:**
- Mobile-first approach
- Adaptive layout: 1 column (mobile), 2 columns (tablet), 3 columns (desktop)
- Cross-browser compatibility (Chrome, Firefox, Safari, Edge)

**User Feedback System:**
- Clear success/error messages for all actions
- Plain English used (no technical jargon)
- Status explanations with next steps
- Contextual help and tooltips

### 5.2 Security Standards

**Authentication & Authorisation:**
- Users can only access their own sessions (Phase 1)
- CSRF protection on all forms
- XSS prevention in templates
- Proper authentication required for all views

**Data Protection:**
- SQL injection prevention through ORM
- Input validation on all forms
- Session data validated before save
- Audit logging for sensitive operations

### 5.3 Testing Standards

**Required Test Coverage:**
- Unit tests for all models, views, and forms
- Integration tests for complete workflows
- Performance tests for dashboard and search functionality
- Accessibility testing with automated tools
- Cross-browser testing

**Testing Framework:**
- Django's built-in test framework
- Factory Boy for test data generation
- Coverage.py for test coverage measurement
- Selenium for end-to-end testing

### 5.4 Code Quality Standards

**Code Style:**
- PEP 8 compliance
- Type hints where appropriate
- Comprehensive docstrings
- Meaningful variable and function names

**Architecture:**
- Django best practices
- DRY (Don't Repeat Yourself) principle
- SOLID principles where applicable
- Clear separation of concerns between apps

## 6. Implementation Plan

### 6.1 Phase 1 Implementation Sequence

1.  **Project Setup**
    *   Initialize Django project (`django-admin startproject thesis_grey_project`).
    *   Configure PostgreSQL database in `settings.py`.
    *   Set up initial Django apps (`python manage.py startapp accounts`, etc.).
    *   Define core models and run initial migrations (`python manage.py makemigrations`, `python manage.py migrate`).
    *   Configure Django's built-in authentication.
    *   Set up Celery with a broker (e.g., Redis).

2.  **Core Feature Implementation (Iterative, per app)**
    *   **Authentication System (`accounts` app):**
        *   Templates for login, signup, profile.
        *   Views for user actions.
    *   **Review Manager Dashboard (`review_manager` app):**
        *   Models, views, templates for session listing and creation.
        *   Status workflow implementation.
        *   Session CRUD operations.
    *   **Search Strategy (`search_strategy` app):**
        *   Models, forms, views, templates for strategy definition.
    *   **SERP Execution (`serp_execution` app):**
        *   Celery tasks for API calls.
        *   Models for tracking execution.
        *   Views and templates for status display.
    *   **Results Manager (`results_manager` app):**
        *   Celery tasks or management commands for processing.
        *   Models for processed results.
    *   **Review Results (`review_results` app):**
        *   Views, forms, templates for reviewing, tagging, noting.
    *   **Reporting (`reporting` app):**
        *   Views, templates for statistics and export functionalities.

3.  **Integration & Testing**
    *   Integrate apps via Django's URL routing.
    *   Write unit and integration tests for each app (using Django's test framework).
    *   End-to-end testing.
    *   Performance optimization (e.g., optimizing ORM queries with `select_related`, `prefetch_related`).

4.  **Deployment**
    *   Docker containerization (Dockerfile for Django app, Celery worker, Redis, PostgreSQL).
    *   Deployment configuration (e.g., Gunicorn/Uvicorn, Nginx).

### 6.2 App Development Order

1. **accounts** - Foundation for all user-related functionality
2. **review_manager** - Core session management and dashboard
3. **search_strategy** - Search strategy definition
4. **serp_execution** - API integration and background tasks
5. **results_manager** - Results processing
6. **review_results** - Results review interface
7. **reporting** - Reports and data export

### 6.3 Key Dependencies and Considerations

- **Schema Updates**: The `ReviewTagAssignment` model includes a `reason` field (`reason = models.TextField(blank=True, null=True)`) to store the justification when a result is tagged as "Exclude". This field is required for Exclude tags and optional for others.
- **API Integration**: Proper configuration of the Serper API (API keys in environment variables/Django settings). Python `requests` library for making calls.
- **Background Jobs**: Celery for handling long-running tasks (API calls, results processing). Requires a message broker like Redis or RabbitMQ.
- **Data Flow**: Ensuring proper data flow from search strategy definition through execution, processing, review, and reporting, managed by Django views, models, and Celery tasks.
- **Static Files & Media**: Configure Django for serving static files (CSS, JS) and potentially user-uploaded media if that becomes a feature.
- **Security**: Implement Django's security best practices (CSRF protection, XSS prevention, HTTPS in production).

## 7. Future Expansion (Phase 2)

While Phase 1 focuses on core functionality, the architecture is designed to support future expansion in Phase 2:

**Collaboration Features:**
- Multi-user teams and organisations
- Role-based permissions (Admin, Reviewer, Observer)
- Real-time collaborative review
- Session sharing and visibility controls

**Advanced Features:**
- **Session Hub**: Enhanced central landing page with team views
- **Search Strategy Enhancements**: Advanced operators, strategy templates, saved searches
- **Results Manager Enhancements**: Advanced deduplication algorithms, bulk operations, AI-assisted categorisation
- **Review Results Enhancements**: Custom tagging systems, collaborative review workflows, conflict resolution
- **Reporting Enhancements**: Custom report templates, advanced visualisations, automated report generation

**Technical Enhancements:**
- **REST API Development**: Full API using Django REST Framework for mobile apps and integrations
- **Real-time Updates**: WebSocket support for live collaboration
- **Advanced Search**: Elasticsearch integration for full-text search
- **Cloud Storage**: Integration with cloud storage providers
- **Mobile Apps**: Native mobile applications

## 8. Documentation Structure

### 8.1 Master PRD (This Document)

- Overall project vision and goals
- Cross-app architectural decisions
- Project-wide standards and requirements
- Implementation sequence and dependencies

### 8.2 App-Specific PRDs

Each Django app has a dedicated PRD in `docs/features/{app_name}/{app_name}-prd.md`:

- **Detailed implementation specifications**
- **User acceptance criteria with checkboxes**
- **Technical architecture specific to the app**
- **Testing requirements**
- **Performance benchmarks**
- **Security considerations**
- **UI/UX specifications**

### 8.3 Implementation Tasks

Task tracking documents in `docs/features/{app_name}/tasks-{app_name}-implementation.md`:

- Sprint planning and task breakdown
- Implementation order and dependencies
- Progress tracking with checkboxes  
- Development team assignments

## 9. Conclusion

The Thesis Grey project, leveraging the robust **Django 4.2 framework**, aims to significantly improve the process of finding, managing, and reviewing grey literature for systematic reviews and clinical guidelines. Phase 1 establishes the core functionality and architecture, providing a solid foundation for future enhancements in Phase 2.

The project's modular Django app structure, combined with individual app-specific PRDs, ensures focused development while maintaining overall architectural coherence. The combination of the Django ORM, Celery for background tasks, and PostgreSQL database provides a maintainable, scalable, and extensible codebase that can evolve to meet the needs of researchers in this specialized domain.

**Key Success Factors:**
- Modular app architecture with clear separation of concerns
- Comprehensive documentation at both project and app levels
- User-centered design with measurable acceptance criteria
- Performance and accessibility standards
- Future-proof design for Phase 2 collaboration features
- Robust testing and quality assurance processes

This master PRD serves as the single source of truth for overall project direction, while detailed app-specific PRDs provide the implementation guidance needed by development teams focusing on individual features.
