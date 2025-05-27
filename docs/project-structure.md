# Project Structure: Thesis Grey

This document outlines the main directory and file structure for the Thesis Grey Django project.

## Root Directory (`d:/Python/Projects/thesis-django`)

*   `.env`: Environment variables (local, not committed).
*   `.env.example`: Example environment variables.
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.
*   `.pre-commit-config.yaml`: Configuration for pre-commit hooks.
*   `.roomodes`: Roo Code modes configuration.
*   `.taskmasterconfig`: Taskmaster tool configuration.
*   `manage.py`: Django's command-line utility for administrative tasks.
*   `pytest.ini`: Configuration for pytest.
*   `mypy.ini`: Configuration for MyPy static type checker.
*   `README.md`: Project overview and setup instructions.
*   `setup_dev.bat` / `setup_dev.sh`: Development environment setup scripts.

## Core Application Directories

### `thesis_grey/` (Django Project Directory)

This is the main Django project configuration directory.

*   `__init__.py`: Marks this directory as a Python package.
*   `settings/`: Contains Django settings modules.
    *   `__init__.py`
    *   `base.py` (Common settings - *assuming this will be created*)
    *   `development.py` (Development specific settings - *assuming*)
    *   `production.py` (Production specific settings - *assuming*)
    *   `testing.py`: Settings for running tests.
*   `urls.py`: Project-level URL configurations.
*   `wsgi.py`: WSGI entry-point for web servers.
*   `asgi.py`: ASGI entry-point for asynchronous features.
*   `health_urls.py`: URLs for health checks.

### Application Directories (Django Apps)

Standard Django applications will reside at the root level alongside `thesis_grey/`.

#### `accounts/` (Planned)

Handles user authentication, registration, profiles, etc. (as per story [`docs/stories/story_auth_registration.md`](docs/stories/story_auth_registration.md:77))

*   `__init__.py`
*   `admin.py`: Admin site configurations for the app.
*   `apps.py`: Application configuration.
*   `forms.py`: Django forms (e.g., registration, login).
*   `models.py`: Database models for the app.
*   `tests.py` / `test_*.py` / `tests/`: Unit and integration tests.
*   `urls.py`: App-specific URL configurations.
*   `views.py`: View functions/classes for handling requests.
*   `templates/accounts/`: HTML templates specific to the accounts app (e.g., `signup.html`, `login.html`).

#### `api/`

Handles API endpoints for the application.

*   `__init__.py`
*   `v1/`: Version 1 of the API.
    *   `__init__.py`
    *   `urls.py`: URL configurations for API v1.
    *   `serializers.py`: (Likely needed) Django REST framework serializers.
    *   `views.py`: (Likely needed) API viewsets or API views.
*   Other app-specific files (`models.py`, `tests.py`, etc. if it's a full Django app).

#### *(Other future application directories will follow this pattern)*

## Supporting Directories

### `bmad-agent/`

Contains files related to the BMad AI agent orchestration.

*   `checklists/`: Various checklists for development processes.
*   `data/`: Knowledge bases and data for agents.
*   `personas/`: Definitions for different AI agent personas.
*   `tasks/`: Definitions for tasks executable by agents.
*   `templates/`: Templates used by agents for document generation.

### `docs/`

Project documentation.

*   `stories/`: User stories.
    *   `story_auth_registration.md`
    *   `story_auth_login.md`
    *   ...
*   `project-structure.md`: This file.
*   `PROJECT_SUMMARY.md`: Overview of the project.
*   `PRD.md`: Product Requirements Document.
*   `ARCHITECTURE.md`: High-level system architecture.
*   `operational-guidelines.md`: (To be reviewed) Coding standards, testing strategy, etc.
*   `tech-stack.md`: (To be reviewed) Details of technologies used.
*   (Other documentation files as needed)

### `requirements/`

Python dependency files.

*   `base.txt`: Core dependencies.
*   `development.txt`: Dependencies for development.
*   `production.txt`: Dependencies for production.
*   `testing.txt`: Dependencies for testing.

### `scripts/`

Utility scripts for the project.

*   `example_prd.txt`: Example PRD.

### `static/` (Convention, if not yet present)

Will contain static files (CSS, JavaScript, images) shared across the project. Each app might also have its own `static/` subdirectory.

### `templates/` (Convention, if not yet present at root)

Project-wide HTML templates (e.g., `base.html`, `404.html`, `500.html`). Each app will also have its own `templates/` subdirectory for app-specific templates.