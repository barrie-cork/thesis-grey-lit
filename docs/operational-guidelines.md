# Operational Guidelines: Thesis Grey

This document outlines the coding standards, testing strategy, error handling, security practices, and other operational guidelines for the Thesis Grey project. Adherence to these guidelines is crucial for maintaining code quality, consistency, and security.

## 1. Coding Standards

### 1.1. Python & Django
    - **PEP 8:** All Python code MUST adhere to [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).
    - **Django Best Practices:** Follow established Django best practices, such as:
        - "Fat Models, Thin Views": Business logic should primarily reside in models or service layers, not views.
        - Keep views and templates simple and focused on presentation.
        - Utilize Django's ORM effectively and efficiently. Avoid raw SQL queries unless absolutely necessary and approved.
        - Use Django's built-in class-based views (CBVs) or function-based views (FBVs) appropriately.
    - **Naming Conventions:**
        - Modules: `lowercase_with_underscores`
        - Classes: `CapWords` (e.g., `UserRegistrationForm`)
        - Functions/Methods: `lowercase_with_underscores` (e.g., `def process_registration():`)
        - Variables: `lowercase_with_underscores`
        - Constants: `UPPERCASE_WITH_UNDERSCORES` (e.g., `MAX_LOGIN_ATTEMPTS = 5`)
    - **Comments & Docstrings:**
        - Write clear and concise comments to explain complex or non-obvious code sections.
        - Use docstrings for all modules, classes, functions, and methods, following [PEP 257 -- Docstring Conventions](https://www.python.org/dev/peps/pep-0257/).
    - **Imports:**
        - Order imports as follows: standard library, third-party libraries, local application/library specific. Separate groups with a blank line.
        - Use absolute imports where possible.
    - **Configuration:**
        - Store configuration settings in Django's `settings.py` files (split into `base.py`, `development.py`, `production.py` as per project structure).
        - Use environment variables for sensitive information (e.g., API keys, database credentials) via `.env` files, loaded by `python-decouple` or similar.

### 1.2. HTML/Templates
    - Use Django Template Language (DTL).
    - Keep templates clean and focused on presentation. Avoid complex logic in templates; move it to views or template tags/filters.
    - Use template inheritance (`{% extends %}`, `{% block %}`) for reusability.
    - Ensure HTML is well-formed and semantically correct.

### 1.3. CSS/JavaScript
    - (To be defined if/when a frontend framework like React/Vue is introduced, or if significant custom CSS/JS is planned).
    - For now, if using vanilla CSS/JS with Django templates, keep them organized, possibly within app-specific `static` directories.

## 2. Testing Strategy

### 2.1. General Principles
    - **Test Coverage:** Aim for high test coverage for all new and modified code. Specific coverage targets may be set by the team.
    - **Test Granularity:** Write tests at different levels:
        - **Unit Tests:** Test individual functions, methods, or classes in isolation.
        - **Integration Tests:** Test interactions between components (e.g., view interacting with a form and model).
    - **Test Location:** Tests for an app should reside within that app's `tests.py` file or a `tests/` subdirectory (e.g., `tests/test_models.py`, `tests/test_views.py`).
    - **Test Naming:** Test functions/methods should start with `test_`.
    - **Assertions:** Use Django's `TestCase` assertions or `pytest` assertions.

### 2.2. Tools
    - **Pytest:** The primary testing framework for this project.
    - **Coverage.py:** To measure test coverage.

### 2.3. What to Test
    - **Models:** Test model methods, custom managers, and any complex field validations.
    - **Forms:** Test form validation, cleaning methods, and saving logic.
    - **Views:** Test view logic, request handling, context data, template rendering, and redirects. Use Django's test client.
    - **APIs:** Test API endpoints for correct responses, status codes, authentication, and authorization.
    - **Services/Utils:** Test any utility functions or service layer components.

## 3. Error Handling & Logging

### 3.1. Error Handling
    - Use specific exception types where possible. Define custom exceptions if necessary for application-specific errors.
    - Handle exceptions gracefully. Avoid bare `except:` clauses.
    - Provide clear, user-friendly error messages for issues originating from user input or actions.
    - For unexpected server errors, log detailed information and return a generic error page/response to the user.
    - Utilize Django's built-in error views (400, 403, 404, 500) and customize them as needed.

### 3.2. Logging
    - Configure Django's logging framework in `settings.py`.
    - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    - Log important events, errors, and exceptions with sufficient context (e.g., traceback, relevant data).
    - Avoid logging sensitive information (passwords, API keys) unless absolutely necessary for debugging in a secure, controlled environment.

## 4. Security Practices

### 4.1. General
    - **Input Validation:** Validate all user-supplied data on both client-side (for UX) and server-side (for security).
    - **Output Encoding:** Ensure proper output encoding to prevent XSS attacks (Django templates do this by default for DTL).
    - **Principle of Least Privilege:** Users and system components should only have the permissions necessary to perform their tasks.

### 4.2. Django Specific
    - **CSRF Protection:** Ensure Django's CSRF protection is enabled and used for all state-changing requests.
    - **XSS Protection:** Rely on Django's template auto-escaping. Be cautious when using `{% autoescape off %}` or `mark_safe`.
    - **SQL Injection:** Use Django's ORM; avoid raw SQL where possible. If raw SQL is used, ensure proper parameterization.
    - **Password Hashing:** Django handles this automatically. Ensure strong password policies are considered (see Story AUTH-001, AC8).
    - **Session Management:** Use Django's secure session management.
    - **HTTPS:** Enforce HTTPS in production.
    - **Debug Mode:** `DEBUG` setting MUST be `False` in production.
    - **Secret Key:** Keep the `SECRET_KEY` confidential and unique for production.

### 4.3. Dependencies
    - Keep dependencies up-to-date to patch known vulnerabilities.
    - Regularly review dependencies for security advisories (e.g., using `pip-audit` or GitHub Dependabot).
    - Only use trusted third-party libraries.

## 5. Version Control (Git)

### 5.1. Branching Strategy
    - `main` (or `master`): Represents the production-ready code. Direct commits are forbidden.
    - `develop`: Integration branch for features.
    - **Feature Branches:** Create new branches from `develop` for each new feature or story (e.g., `feature/AUTH-001-registration`, `fix/some-bug`).
    - **Hotfix Branches:** Branched from `main` for critical production bugs, then merged back into `main` and `develop`.

### 5.2. Commits
    - Make small, atomic commits.
    - Write clear, concise commit messages following a convention (e.g., Conventional Commits: `feat: Add user registration form`).
        - Subject line: Imperative mood, max 50 chars.
        - Body (optional): Explain *what* and *why* vs. *how*.

### 5.3. Pull Requests (PRs) / Merge Requests (MRs)
    - All feature branches must be merged into `develop` via PRs/MRs.
    - PRs must be reviewed by at least one other team member before merging.
    - Ensure all tests pass and linting checks are clean before requesting a review.
    - PR descriptions should clearly explain the changes and reference the relevant story/issue.

## 6. Code Reviews
    - **Purpose:** Improve code quality, share knowledge, ensure adherence to standards, and catch bugs early.
    - **Focus Areas:**
        - Correctness and completeness of the implementation against requirements.
        - Adherence to coding standards and operational guidelines.
        - Test coverage and quality.
        - Security implications.
        - Readability and maintainability.
        - Performance considerations.
    - Be constructive and respectful in review comments.

## 7. Static Analysis & Linting
    - **Flake8/Pylint:** Use for Python linting to enforce PEP 8 and catch common errors.
    - **MyPy:** Use for static type checking to catch type errors.
    - **Pre-commit Hooks:** Configure pre-commit hooks (using `.pre-commit-config.yaml`) to run linters and formatters automatically before commits.

## 8. Documentation
    - Keep project documentation (this file, `project-structure.md`, `ARCHITECTURE.md`, `PRD.md`, etc.) up-to-date.
    - Document new features, architectural decisions, and complex parts of the system.
    - User stories should be detailed and include clear Acceptance Criteria.