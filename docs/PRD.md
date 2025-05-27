# Thesis Grey: Master Project Plan (Django Edition)

**Project Title:** Thesis Grey
**Version:** 1.0
**Date:** 2025-05-26
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
- **Frontend:** Django Templates, HTML, CSS (potentially TailwindCSS), JavaScript (for interactivity)
- **Backend:** Django, Django ORM
- **Database:** PostgreSQL (using Psycopg 3)
- **APIs:** Google Search API via Serper (using a Python client like `requests`)
- **Background Tasks:** Celery with Redis or RabbitMQ as a broker
- **DevOps:** Docker, GitHub Actions (basic CI/CD)
- **API Development (Optional for Phase 1, core for Phase 2):** Django REST Framework

### 3.2 Architectural Approach

The project will adopt a **modular design using Django Apps**. Each core feature or domain will be encapsulated within its own app, promoting separation of concerns and maintainability. While Django's app structure provides a natural way to organize by feature, the principles of **Vertical Slice Architecture** will still guide development, focusing on implementing features end-to-end. This allows implementation to focus on one feature at a time, ensuring the feature in focus passes all tests before moving to the next. This should guide the roadmap.

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

- `User`: Stores user authentication and profile information (likely extending Django's built-in `AbstractUser`). `db_comment` will be used for clarity.
- `SearchSession`: Represents a review session with its search strategy. `db_table_comment` and `db_comment` on fields will be used.
- `SearchQuery`: Defines specific queries within a session.
- `SearchExecution`: Tracks the execution of search queries.
- `RawSearchResult`: Stores raw data from search engines.
- `ProcessedResult`: Contains normalized and processed search results.
- `DuplicateRelationship`: Tracks duplicate results.
- `ReviewTag`: Defines tags for categorizing results (Include, Exclude, Maybe).
- `ReviewTagAssignment`: Links tags to results.
- `Note`: Stores notes added to results.

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

**Description:** Central landing page displaying the user's review sessions and allowing creation of new sessions.

**Key Components (Django context):**
- `ReviewManagerDashboardView` (Class-Based View or function view).
- Django template for the dashboard.
- Django ORM queries to fetch `SearchSession` objects for the user.
- Django Form for creating new sessions.

**Technical Implementation:**
- Sessions displayed by status (Draft, In Progress, Completed) via ORM filtering.
- Navigation to appropriate feature page based on status using Django's URL routing.

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
- Inline tagging system (Include, Exclude, Maybe) via Django Forms and views.
- Exclusion reason capture when tagging as "Exclude".
- Simple notes system integrated directly within the results view.
- PRISMA-compliant workflow.

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

## 5. Implementation Plan

### 5.1 Phase 1 Implementation Sequence

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

### 5.2 Key Dependencies and Considerations

- **Schema Updates**: The `ReviewTagAssignment` model needs an optional `reason` field (e.g., `reason = models.TextField(blank=True, null=True)`) added to store the justification when a result is tagged as "Exclude".
- **API Integration**: Proper configuration of the Serper API (API keys in environment variables/Django settings). Python `requests` library for making calls.
- **Background Jobs**: Celery for handling long-running tasks (API calls, results processing). Requires a message broker like Redis or RabbitMQ.
- **Data Flow**: Ensuring proper data flow from search strategy definition through execution, processing, review, and reporting, managed by Django views, models, and Celery tasks.
- **Static Files & Media**: Configure Django for serving static files (CSS, JS) and potentially user-uploaded media if that becomes a feature.
- **Security**: Implement Django's security best practices (CSRF protection, XSS prevention, HTTPS in production).

## 6. Future Expansion (Phase 2)

While Phase 1 focuses on core functionality, the architecture is designed to support future expansion in Phase 2:

- **Session Hub**: Enhanced central landing page.
- **Search Strategy Enhancements**: Advanced operators, templates.
- **Results Manager Enhancements**: Advanced deduplication, bulk operations.
- **Review Results Enhancements**: Custom tagging, collaborative review.
- **Reporting Enhancements**: Custom templates, advanced visualizations.
- **REST API Development**: Exposing functionalities via Django REST Framework for potential third-party integrations or a decoupled frontend.

## 7. Conclusion

The Thesis Grey project, leveraging the robust **Django 4.2 framework**, aims to significantly improve the process of finding, managing, and reviewing grey literature for systematic reviews and clinical guidelines. Phase 1 establishes the core functionality and architecture, providing a solid foundation for future enhancements in Phase 2.

The project's modular Django app structure, combined with the power of the Django ORM, Celery for background tasks, and PostgreSQL database, ensures a maintainable, scalable, and extensible codebase that can evolve to meet the needs of researchers in this specialized domain.