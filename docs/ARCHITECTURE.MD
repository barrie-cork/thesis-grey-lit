# Thesis Grey: Software Architecture Document

**Version:** 1.0
**Date:** 2025-05-26
**Project:** Thesis Grey
**Source PRD:** [`PRD.md`](PRD.md) (Version 1.0, 2025-05-26)

## 1. Introduction

### 1.1. Purpose
This document outlines the software architecture for the "Thesis Grey" project. It details the system's structure, components, interactions, and the technologies used. This architecture is derived from the requirements and goals specified in the Project Requirements Document ([`PRD.md`](PRD.md)).

### 1.2. Project Overview
Thesis Grey is a specialized web application designed to help researchers systematically find, manage, and review "grey literature." Built using the Django 4.2 framework, it aims to streamline the creation of search strategies, automate search execution (initially via Google Search API - Serper), and organize results for review, adhering to best practices like PRISMA.

### 1.3. Scope
This document covers the architecture for Phase 1 of the Thesis Grey project as defined in the [`PRD.md`](PRD.md).

## 2. Architectural Goals & Constraints

### 2.1. Goals
The architecture is designed to achieve the following primary goals for Phase 1 (derived from [`PRD.md`](PRD.md) Section 2):
1.  Provide researchers with tools to create and execute systematic search strategies.
2.  Enable efficient processing and review of search results.
3.  Support PRISMA-compliant workflows for literature reviews.
4.  Establish a foundation that can be extended in Phase 2 without significant refactoring.

### 2.2. Constraints
The architecture adheres to the following key constraints:
1.  **Framework:** Strictly Django `4.2.x` (Python), as per user directive and [`PRD.md`](PRD.md).
2.  **Database:** PostgreSQL (using Psycopg 3) ([`PRD.md`](PRD.md)).
3.  **Background Tasks:** Celery with Redis as the message broker ([`PRD.md`](PRD.md)).
4.  **External APIs:** Google Search API via Serper ([`PRD.md`](PRD.md)).
5.  **Development Environment:** Docker for containerization ([`PRD.md`](PRD.md)).

## 3. Guiding Principles

The following principles guide the architectural design:
1.  **Modularity:** The system is decomposed into distinct Django Apps, each encapsulating a core feature or domain, promoting separation of concerns and maintainability ([`PRD.md`](PRD.md)).
2.  **Vertical Slice Architecture:** Development will focus on implementing features end-to-end (UI to database, including tests) one at a time, ensuring each slice is functional and tested before moving to the next ([`PRD.md`](PRD.md)).
3.  **Testability:** Emphasis on unit and integration tests for each app using Django's test framework to ensure reliability and maintain code quality ([`PRD.md`](PRD.md)).
4.  **Maintainability & Extensibility:** The chosen structure and technologies aim for a codebase that is easy to understand, modify, and extend for future phases ([`PRD.md`](PRD.md)).
5.  **Adherence to Django Best Practices:** Leveraging Django's built-in features and conventions where possible.

## 4. Technology Stack

The technology stack for Phase 1 is defined as follows (from [`PRD.md`](PRD.md) Section 3.1):
-   **Framework:** Django `4.2.x` (Python)
-   **Frontend:** Django Templates, HTML, CSS (with TailwindCSS), JavaScript (for AJAX interactivity)
-   **Backend:** Django, Django ORM
-   **Database:** PostgreSQL (using Psycopg 3)
-   **APIs (External):** Google Search API via Serper (using a Python client like `requests`)
-   **Background Tasks:** Celery with Redis as the message broker
-   **DevOps:** Docker, GitHub Actions (basic CI/CD)
-   **API Development (Internal - Phase 1):** Django built-in JSON responses for AJAX functionality, Django REST Framework for Phase 2 if needed

## 5. System Architecture Overview

### 5.1. Logical Architecture
The system comprises several key logical components that interact to deliver the required functionality:

```mermaid
graph TD
    A[User/Researcher] --> B{Web Browser};
    B --> C[Django Web Application (Thesis Grey)];
    C --> D[PostgreSQL Database];
    C --> E[Celery Beat (Scheduler)];
    E --> F[Celery Workers];
    F --> C;
    F --> G[Serper API (Google Search)];
    F --> D;
    H[Redis/RabbitMQ (Celery Broker)] --> F;
    F --> H;
    E --> H;

    subgraph "Django Web Application (Thesis Grey)"
        C1[Presentation Layer (Django Templates & Views)]
        C2[Application Logic (Django Apps & Services)]
        C3[Data Access Layer (Django ORM)]
    end

    C1 --> C2;
    C2 --> C3;
    C3 --> D;
    C2 --> F;
```

**Component Descriptions:**
-   **Web Browser:** The client interface for researchers.
-   **Django Web Application (Thesis Grey):** The core application handling user requests, business logic, and data management.
    -   **Presentation Layer:** Renders HTML pages using Django Templates.
    -   **Application Logic:** Encapsulated within Django Apps, handles core features.
    -   **Data Access Layer:** Interacts with the database via Django ORM.
-   **PostgreSQL Database:** Persistent storage for all application data.
-   **Celery Beat:** Schedules periodic tasks (if any).
-   **Celery Workers:** Execute background tasks asynchronously (e.g., API calls, data processing).
-   **Redis/RabbitMQ:** Message broker for Celery.
-   **Serper API:** External service for executing Google searches.

### 5.2. Django Application Architecture
The project will be organized into a main Django project (`thesis_grey_project`) and a collection of Django apps located in an `apps/` directory at the project root, as illustrated in [`PRD-D.md`](PRD-D.md:48) Section 3.3.

**Main Project (`thesis_grey_project`):**
-   Handles global configurations (settings, project-level URLs).
-   WSGI/ASGI entry points.

**Feature-Specific Apps (within `apps/` directory):**
Each app encapsulates a distinct area of functionality:
1.  **`accounts`:** User authentication (registration, login, profile management) using Django's built-in auth system.
2.  **`review_manager`:** Review Manager Dashboard, creation and listing of `SearchSession` objects. **Contains the SearchSession model** with future-proof collaboration fields for Phase 2.
3.  **`search_strategy`:** Definition and management of search strategies (PIC framework, parameters) within a `SearchSession` (imports model from review_manager).
4.  **`serp_execution`:** Handles the execution of search queries against the Serper API via Celery tasks, tracks `SearchExecution` status, and stores `RawSearchResult`.
5.  **`results_manager`:** Processes `RawSearchResult` into `ProcessedResult`, including normalization and basic deduplication.
6.  **`review_results`:** Interface for reviewing `ProcessedResult`, applying `ReviewTag` (Include, Exclude, Maybe), and adding `Note` objects.
7.  **`reporting`:** Generates reports, PRISMA flow statistics, and data export (CSV, JSON, PDF).

Each app will follow the standard Django app structure outlined in [`PRD.md`](PRD.md) Section 3.4 (models, views, forms, templates, urls, tests, etc.).

### 5.3. Deployment View (Conceptual)
Phase 1 deployment will utilize Docker for containerization ([`PRD.md`](PRD.md)):
-   A Docker container for the Django web application (running with Gunicorn or Uvicorn).
-   A Docker container for Celery worker(s).
-   A Docker container for the Celery Beat scheduler (if needed).
-   A Docker container for the PostgreSQL database.
-   A Docker container for the Redis/RabbitMQ message broker.
-   Nginx will likely be used as a reverse proxy and for serving static files in a production-like environment.

## 6. Data Architecture

### 6.1. Database
PostgreSQL will be used as the relational database, managed via the Django ORM ([`PRD.md`](PRD.md)).

### 6.2. ORM
The Django Object-Relational Mapper (ORM) will be used for all database interactions, simplifying data access and ensuring database-agnostic query construction where possible. Django's migration system will manage schema changes.

### 6.3. Core Entities & Relationships
The core data model for Phase 1 (designed to support both phases) includes the following entities, as detailed in [`PRD.md`](PRD.md) Section 3.4. `db_table_comment` and `db_comment` will be utilized on models and fields respectively for clarity.

```mermaid
erDiagram
    User {
        int id PK "db_comment: Primary key"
        string username "db_comment: Unique username"
        string password "db_comment: Hashed password"
        string email "db_comment: User's email"
        string first_name "db_comment: Optional first name"
        string last_name "db_comment: Optional last name"
        bool is_active "db_comment: Designates whether this user should be treated as active"
        bool is_staff "db_comment: Designates whether the user can log into this admin site"
        datetime date_joined "db_comment: The date the user was created"
        "db_table_comment: Stores user authentication and profile information"
    }

    SearchSession {
        int id PK "db_comment: Primary key"
        int created_by_id FK "db_comment: Foreign key to User who created session"
        int lead_reviewer_id FK "db_comment: Foreign key to User (current lead reviewer)"
        string title "db_comment: Title of the search session"
        string description "db_comment: Description of the search session"
        string population_terms "db_comment: PIC - Population terms"
        string interest_terms "db_comment: PIC - Interest terms"
        string context_terms "db_comment: PIC - Context terms"
        string status "db_comment: 9-state workflow: draft, strategy_ready, executing, processing, ready_for_review, in_review, completed, failed, archived"
        bool is_collaborative "db_comment: Phase 2 - Whether session allows multiple reviewers"
        datetime review_deadline "db_comment: Phase 2 - Optional deadline for collaborative review"
        datetime created_at "db_comment: Timestamp of creation"
        datetime updated_at "db_comment: Timestamp of last update"
        "db_table_comment: Represents a review session with search strategy and Phase 2 collaboration support"
    }

    SearchQuery {
        int id PK "db_comment: Primary key"
        int session_id FK "db_comment: Foreign key to SearchSession"
        string query_string "db_comment: The actual search query string"
        string search_engine "db_comment: e.g., Google (via Serper)"
        datetime created_at "db_comment: Timestamp of creation"
        "db_table_comment: Defines specific queries within a session"
    }

    SearchExecution {
        int id PK "db_comment: Primary key"
        int query_id FK "db_comment: Foreign key to SearchQuery"
        string status "db_comment: e.g., Pending, Running, Completed, Failed"
        datetime started_at "db_comment: Timestamp when execution started"
        datetime completed_at "db_comment: Timestamp when execution completed"
        string error_message "db_comment: Error message if execution failed (nullable)"
        "db_table_comment: Tracks the execution of search queries"
    }

    RawSearchResult {
        int id PK "db_comment: Primary key"
        int execution_id FK "db_comment: Foreign key to SearchExecution"
        string url "db_comment: URL of the search result"
        string title "db_comment: Title of the search result"
        string snippet "db_comment: Snippet or abstract from the search result"
        json raw_data "db_comment: Raw JSON data from the search engine API"
        datetime retrieved_at "db_comment: Timestamp when result was retrieved"
        "db_table_comment: Stores raw data from search engines"
    }

    ProcessedResult {
        int id PK "db_comment: Primary key"
        int session_id FK "db_comment: Foreign key to SearchSession (denormalized for easier querying within a session)"
        string normalized_url "db_comment: Normalized URL for deduplication"
        string title "db_comment: Processed title"
        string snippet "db_comment: Processed snippet"
        string source_type "db_comment: e.g., Report, Thesis, Conference (inferred or manual)"
        bool is_duplicate "db_comment: Flag indicating if it's a duplicate"
        datetime processed_at "db_comment: Timestamp when result was processed"
        "db_table_comment: Contains normalized and processed search results"
    }

    DuplicateRelationship {
        int id PK "db_comment: Primary key"
        int original_result_id FK "db_comment: Foreign key to ProcessedResult (the original)"
        int duplicate_result_id FK "db_comment: Foreign key to ProcessedResult (the duplicate)"
        string method "db_comment: Deduplication method used (e.g., URL normalization)"
        datetime created_at "db_comment: Timestamp of relationship creation"
        "db_table_comment: Tracks duplicate results"
    }

    ReviewTag {
        int id PK "db_comment: Primary key"
        string name "db_comment: Tag name (e.g., Include, Exclude, Maybe)"
        string description "db_comment: Description of the tag (nullable)"
        "db_table_comment: Defines tags for categorizing results"
    }

    ReviewTagAssignment {
        int id PK "db_comment: Primary key"
        int result_id FK "db_comment: Foreign key to ProcessedResult"
        int tag_id FK "db_comment: Foreign key to ReviewTag"
        int user_id FK "db_comment: Foreign key to User (who assigned the tag)"
        string reason "db_comment: Justification if tagged as Exclude (nullable, as per PRD 5.2)"
        datetime assigned_at "db_comment: Timestamp of assignment"
        "db_table_comment: Links tags to results"
    }

    Note {
        int id PK "db_comment: Primary key"
        int result_id FK "db_comment: Foreign key to ProcessedResult"
        int user_id FK "db_comment: Foreign key to User (who wrote the note)"
        text content "db_comment: Content of the note"
        datetime created_at "db_comment: Timestamp of creation"
        datetime updated_at "db_comment: Timestamp of last update"
        "db_table_comment: Stores notes added to results"
    }

    SessionCollaborator {
        int id PK "db_comment: Primary key"
        int session_id FK "db_comment: Foreign key to SearchSession"
        int user_id FK "db_comment: Foreign key to User (collaborator)"
        int invited_by_id FK "db_comment: Foreign key to User (who sent invitation)"
        string role "db_comment: Phase 2 - viewer, reviewer, editor, lead"
        datetime invited_at "db_comment: When invitation was sent"
        datetime accepted_at "db_comment: When invitation was accepted (null = pending)"
        "db_table_comment: Phase 2 - Collaboration relationships for review sessions"
    }

    User ||--o{ SearchSession : "creates"
    User ||--o{ SearchSession : "leads"
    SearchSession ||--o{ SessionCollaborator : "has_collaborators"
    User ||--o{ SessionCollaborator : "collaborates_on"
    User ||--o{ SessionCollaborator : "invites_to"
    SearchSession ||--o{ SearchQuery : "contains"
    SearchQuery ||--o{ SearchExecution : "executes"
    SearchExecution ||--o{ RawSearchResult : "yields"
    SearchSession ||--o{ ProcessedResult : "aggregates"
    ProcessedResult ||--o{ ReviewTagAssignment : "has"
    ReviewTag ||--o{ ReviewTagAssignment : "is_assigned_via"
    User ||--o{ ReviewTagAssignment : "assigns"
    ProcessedResult ||--o{ Note : "has"
    User ||--o{ Note : "writes"
    ProcessedResult ||--o{ DuplicateRelationship : "can_be_original_in"
    ProcessedResult ||--o{ DuplicateRelationship : "can_be_duplicate_in"
```

**Key Relationships:**
-   A `User` can have multiple `SearchSession`s.
-   A `SearchSession` comprises multiple `SearchQuery`s.
-   Each `SearchQuery` leads to one or more `SearchExecution`s (e.g., if retried).
-   An `SearchExecution` yields multiple `RawSearchResult`s.
-   `RawSearchResult`s are processed into `ProcessedResult`s, associated with the parent `SearchSession`.
-   `ProcessedResult`s can be tagged (via `ReviewTagAssignment`) and annotated with `Note`s.
-   `DuplicateRelationship` links `ProcessedResult`s that are identified as duplicates.

## 7. Key Component Design & Data Flow

This section elaborates on the architectural aspects of core features outlined in [`PRD.md`](PRD.md) Section 4.

### 7.1. Authentication (`accounts` app)
-   **Implementation:** Leverages Django's built-in authentication system (`django.contrib.auth`).
-   **User Model:** May extend `AbstractUser` if additional user-specific fields are required beyond basic profile information.
-   **Views:** Standard `LoginView`, `LogoutView`, plus custom views for registration (`UserCreationForm`) and profile management.
-   **Templates:** Custom HTML templates for login, signup, and profile pages.

### 7.2. Review Manager Dashboard (`review_manager` app)
-   **Views:** Multiple Class-Based Views for comprehensive session management:
    -   `DashboardView`: Main landing page with session cards grouped by status
    -   `SessionCreateView`: Two-step creation (minimal → redirect to strategy)
    -   `SessionDetailView`, `SessionUpdateView`, `SessionDeleteView`: Full CRUD operations
-   **Smart Navigation:** Sessions route users to next logical step based on 9-state status workflow
-   **Data Flow:**
    1.  User navigates to dashboard with optimised queries (select_related, prefetch_related)
    2.  Sessions displayed in responsive card layout grouped by Active, Completed, Failed
    3.  Session creation: minimal form (title + description) → immediate redirect to search strategy
    4.  Session management: delete drafts only, archive completed sessions, duplicate any session

### 7.3. Search Strategy (`search_strategy` app)
-   **View:** A view (CBV or function-based) to handle creation and editing of search strategy details within a `SearchSession`.
-   **Form:** A `ModelForm` for the `SearchSession` fields related to strategy (PIC terms, parameters).
-   **Data Flow (Strategy Definition & Execution Trigger):**
    1.  User defines/edits strategy via the form.
    2.  On submission, form data updates the `SearchSession` instance.
    3.  If the user initiates execution, the view triggers a Celery task (e.g., `initiate_search_session_execution_task`) passing the `SearchSession` ID.

### 7.4. SERP Execution (`serp_execution` app)
-   **Celery Task (`perform_serp_query_task`):**
    -   Accepts a `SearchQuery` ID (or details).
    -   Makes HTTP calls to the Serper API using `requests`.
    -   Handles API responses, rate limiting (if applicable), and errors.
    -   Stores results as `RawSearchResult` objects, linked to a `SearchExecution` record.
    -   Updates `SearchExecution` status (Pending, Running, Completed, Failed).
-   **View (`SearchExecutionStatusView`):** Displays the progress of active search executions for a session. May use JavaScript polling or (later) WebSockets for updates.
-   **Data Flow:**
    1.  `initiate_search_session_execution_task` (from `search_strategy`) creates `SearchQuery` and `SearchExecution` records.
    2.  It then dispatches one or more `perform_serp_query_task` instances to Celery.
    3.  Celery workers pick up tasks, call Serper API, save `RawSearchResult`.
    4.  Status view polls `SearchExecution` status.
    5.  Once all queries for a session are complete, a subsequent processing task can be triggered.

### 7.5. Results Manager (`results_manager` app)
-   **Celery Task or Management Command (`process_session_results_task`):**
    -   Triggered after SERP execution for a session completes.
    -   Fetches `RawSearchResult`s for the session.
    -   Performs normalization (e.g., URLs) and basic metadata extraction.
    -   Implements deduplication logic (e.g., based on normalized URLs).
    -   Creates/updates `ProcessedResult` objects and `DuplicateRelationship` records.
-   **View (`ResultsOverviewView` - part of `review_results` app):** Displays the `ProcessedResult`s.

### 7.6. Review Results (`review_results` app)
-   **View (`ResultsOverviewView`):**
    -   Displays `ProcessedResult`s for a session, with pagination (Django's `Paginator`).
    -   Integrates Django `Form`s for applying `ReviewTag`s (Include, Exclude, Maybe) and adding `Note`s.
    -   Handles creation/update of `ReviewTagAssignment` (including `reason` for "Exclude") and `Note` objects via AJAX or standard form submissions.
-   **Data Flow:**
    1.  User views paginated list of `ProcessedResult`s.
    2.  User applies a tag or adds a note to a result.
    3.  Form submission (possibly AJAX) updates/creates `ReviewTagAssignment` or `Note` records.
    4.  View refreshes relevant part of the page or reloads.

### 7.7. Reporting (`reporting` app)
-   **View (`ReportingView`):**
    -   Queries `ProcessedResult`, `ReviewTagAssignment`, and other relevant models to aggregate statistics.
    -   Calculates PRISMA flow data (e.g., number of records identified, duplicates removed, screened, included).
    -   Displays summary statistics (tag distribution, domain distribution).
-   **Export Functionality:**
    -   Separate view actions or methods to generate CSV, JSON, and PDF exports.
    -   Uses Python's `csv`, `json` modules.
    -   For PDF, libraries like `ReportLab` or `WeasyPrint` will be used.

## 8. Integration Points

### 8.1. Serper API (Google Search)
-   **Responsibility:** `serp_execution` app's Celery tasks.
-   **Method:** HTTP GET requests using the Python `requests` library.
-   **Authentication:** API key managed via environment variables and accessed through Django settings ([`PRD.md`](PRD.md)).
-   **Error Handling:** Robust error handling for API call failures, rate limits, etc.
-   **Circuit Breaker Consideration (Phase 2):** To prevent repeated calls to a failing Serper API, a circuit breaker mechanism (e.g., using a library like `pybreaker` within Celery tasks) will be considered for Phase 2. For Phase 1, basic error handling and retry logic will be implemented.

### 8.2. Celery (Background Tasks)
-   **Broker:** Redis, configured in Django settings ([`PRD.md`](PRD.md)).
-   **Key Tasks:**
    -   `perform_serp_query_task` (in `serp_execution`): Fetches search results.
    -   `process_session_results_task` (in `results_manager`): Processes raw results.
    -   Potentially other tasks for notifications or scheduled activities.
-   **Monitoring:** Basic Celery monitoring tools (e.g., Flower) can be considered for operational insight.

## 9. Cross-Cutting Concerns

### 9.1. Security
-   Utilize Django's built-in security features: CSRF protection, XSS prevention, clickjacking protection ([`PRD-D.md`](PRD-D.md:299)).
-   Ensure HTTPS is enforced in production environments.
-   Securely manage API keys and sensitive configuration (environment variables).
-   Regularly update dependencies to patch security vulnerabilities.
-   Implement appropriate authorization checks in views (e.g., ensuring users can only access their own data).

### 9.2. Static Files & Media Management
-   Static files (CSS, JavaScript, images) will be managed using Django's `staticfiles` app.
-   During development, Django can serve static files.
-   In production, Nginx or a similar web server will typically serve static files.
-   User-uploaded media is not a core feature for Phase 1 but will be considered if requirements evolve.

### 9.3. Testing Strategy
-   **Unit Tests:** Each app will have comprehensive unit tests for its models, forms, views, and utility functions.
-   **Integration Tests:** Tests to verify interactions between components within an app and between different apps.
-   **Framework:** Django's built-in test framework (`django.test.TestCase`, `RequestFactory`, etc.).
-   **CI/CD:** Basic Continuous Integration via GitHub Actions to run tests on pushes/pull requests ([`PRD-D.md`](PRD-D.md:38)).

### 9.4. Error Handling and Resilience
Beyond standard Django error handling and Celery task retries:

-   **Graceful Degradation Strategies:**
-   **Serper API Unavailability:** If the Serper API is unavailable (e.g., network issues, API downtime, or an open circuit breaker):
    -   New search execution requests will be queued or postponed.
    -   Users will be clearly informed via the UI about the temporary service degradation affecting new searches.
    -   The system will remain functional for all other operations, such as managing existing search sessions, reviewing previously fetched results, and accessing reporting features.
    -   UI elements for initiating new searches might be temporarily disabled or display an advisory message.
-   **Celery/Broker Unavailability:** If background task processing (Celery workers or the message broker) is significantly impaired:
    -   Tasks dependent on Celery (e.g., search execution, results processing) will be queued.
    -   Users will be informed of processing delays through UI notifications.
    -   Core data viewing, strategy definition, and management tasks not requiring immediate background processing should remain operational.
-   **Comprehensive Error Logging:** Ensure detailed logging for errors from external services, background tasks, and critical application paths to facilitate diagnosis and recovery.
-   **User Feedback:** Provide clear, user-friendly error messages when operations cannot be completed, guiding the user on potential next steps or when to expect resolution.

### 9.5. Coding Standards and Conventions

To ensure consistency and maintainability across the "Thesis Grey" codebase, the following standards and conventions will be adhered to:

1.  **Base Standard:** All Python code will strictly adhere to [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).
2.  **Django Conventions:** Standard Django naming conventions and code organization practices will be followed (e.g., model naming, view structure, form handling).
3.  **Naming Conventions (Project Specific):**
    *   **Models:** PascalCase (e.g., `SearchSession`, `ProcessedResult`). Fields will be snake_case.
    *   **Views:** Class-Based Views will be PascalCase ending in `View` (e.g., `SearchSessionListView`). Function-based views will be snake_case.
    *   **Forms:** PascalCase ending in `Form` (e.g., `SearchSessionForm`).
    *   **Templates:** HTML files will be snake_case (e.g., `search_session_list.html`). Template directory structure will mirror app names.
    *   **URLs:** URL names will be snake_case, typically prefixed with the app name (e.g., `accounts:login`, `review_manager:dashboard`).
    *   **Celery Tasks:** snake_case, often ending with `_task` (e.g., `perform_serp_query_task`).
    *   **CSS Classes/IDs:** kebab-case (e.g., `search-session-card`, `btn-primary`). (This can be refined if TailwindCSS is adopted, as it uses utility classes).
4.  **Docstrings and Comments:**
    *   All public modules, classes, functions, and methods will have clear docstrings explaining their purpose, arguments, and return values (if any), following [PEP 257 -- Docstring Conventions](https://www.python.org/dev/peps/pep-0257/).
    *   Comments will be used to explain complex or non-obvious sections of code.
    *   `# TODO:` comments will be used to mark areas needing future attention, ideally with a brief explanation or issue tracker reference.
5.  **Imports:**
    *   Imports will be grouped in the standard order: standard library, third-party, local application/library specific.
    *   Absolute imports are preferred over relative imports for clarity within the project.
6.  **Testing:**
    *   Test methods will be clearly named, indicating what they are testing (e.g., `test_search_session_creation_success`, `test_form_invalid_data`).
    *   Test classes will group related tests for a specific model, view, or form.
7.  **Linters and Formatters:**
    *   Tools like Flake8 (for linting) and Black (for code formatting) will be configured and used to automatically enforce standards and maintain a consistent style. Configuration for these tools will be committed to the repository.

## 10. Future Considerations (Phase 2 Preview)

The current architecture is designed with Phase 2 expansions in mind ([`PRD.md`](PRD.md) Section 6):
-   **REST API Development:** The modular app structure and Django ORM will facilitate the addition of a REST API using Django REST Framework for decoupled frontends or third-party integrations.
-   **Advanced Features:** Enhancements to search strategy, results management, review collaboration, and reporting can be built upon the existing app structures.

## 11. Document History

| Version | Date       | Author(s)      | Changes                                      |
|---------|------------|----------------|----------------------------------------------|
| 1.0     | 2025-05-26 | BMAD Architect | Initial draft based on PRD.md Version 1.0. |