# Thesis Grey: User Stories and Natural Language Requirements (Django Edition)

## Project Overview
Thesis Grey is a specialised web application designed to help researchers systematically find, manage, and review "grey literature" for clinical guideline development. Built using Django 4.2 framework, it streamlines the process of creating search strategies, executing searches, and organising results following PRISMA best practices.

---

## User Authentication & Account Management

### User Stories

**As a researcher**, I want to create an account so that I can access the search application and manage my research sessions.

**As a registered user**, I want to log into the system so that I can access my saved searches and continue my work.

**As a logged-in user**, I want to manage my profile information so that I can keep my account details current.

**As a user**, I want to be automatically redirected to the Review Manager after login so that I can quickly access my work.

### Natural Language Requirements

- The system shall provide a registration form using Django's built-in `UserCreationForm` accepting username, email (optional), and password
- The system shall validate registration inputs using Django form validation and provide clear error messages for invalid data
- The system shall securely hash and store user passwords using Django's built-in password hashing
- The system shall provide a login form using Django's `AuthenticationForm` with username and password fields
- The system shall implement session-based authentication using Django's built-in authentication system
- The system shall automatically redirect authenticated users to the Review Manager dashboard page
- The system shall provide a user profile page where users can update their information using Django ModelForms
- The system shall restrict access to authenticated pages using Django's `@login_required` decorator or `LoginRequiredMixin`
- The system shall provide clear feedback for authentication failures using Django messages framework

---

## Review Manager Dashboard

### User Stories

**As a researcher**, I want to see all my review sessions in one place so that I can quickly access and manage my ongoing work.

**As a researcher**, I want to create a new review session so that I can start a new literature search project.

**As a researcher**, I want to see the status of each review session so that I know which ones need attention.

**As a researcher**, I want to navigate directly to the appropriate page based on my session's status so that I can continue my work efficiently.

### Natural Language Requirements

- The system shall display a central Review Manager dashboard as the main landing page after authentication
- The system shall show all review sessions owned by the authenticated user using Django ORM queries
- The system shall categorise sessions by status (Draft, In Progress, Completed) using Django ORM filtering
- The system shall provide a "Create New Review" form using Django ModelForm for `SearchSession` creation
- The system shall allow users to click on sessions to navigate to appropriate pages using Django URL routing:
  - Draft sessions → Search Strategy page
  - Executing sessions → Search Execution Status page
  - Completed sessions → Results Overview page
- The system shall display basic session information (name, description, creation date, status) using Django templates
- The system shall provide visual indicators for session status using CSS classes and Django template conditionals
- The system shall handle empty states when no sessions exist using Django template logic

---

## Search Strategy Development

### User Stories

**As a researcher**, I want to create and configure search strategies so that I can define what literature to search for.

**As a researcher**, I want to organise my search concepts using the PIC framework (Population, Interest, Context) so that I can structure my search systematically.

**As a researcher**, I want to select specific domains and file types so that I can focus my search on relevant sources.

**As a researcher**, I want to see a preview of my generated queries so that I can understand what will be searched.

**As a researcher**, I want to save my search strategy so that I can execute it later or modify it as needed.

### Natural Language Requirements

- The system shall provide a Search Strategy page accessible from the Review Manager using Django URL routing
- The system shall allow users to enter search terms organised by PIC categories using Django ModelForm:
  - Population: terms describing the target population
  - Interest: terms describing the intervention or phenomenon of interest
  - Context: terms describing the setting or context
- The system shall provide domain selection options using Django ChoiceField or MultipleChoiceField
- The system shall offer file type filtering options (PDF, DOC, HTML, etc.) using Django form fields
- The system shall generate search queries automatically based on entered concepts using Python string manipulation
- The system shall display a real-time preview of generated queries using JavaScript and Django AJAX views
- The system shall validate search strategy inputs using Django form validation and provide helpful error messages
- The system shall save search strategies to the PostgreSQL database using Django ORM when users submit the form
- The system shall allow users to modify existing search strategies for draft sessions using Django UpdateView or custom views
- The system shall provide clear navigation to execute searches using Django URL routing and form actions

---

## Search Execution and Monitoring

### User Stories

**As a researcher**, I want to execute my search strategy across search engines so that I can gather comprehensive results.

**As a researcher**, I want to monitor the progress of my search execution so that I know when it's complete.

**As a researcher**, I want to see if any errors occur during search execution so that I can address them.

**As a researcher**, I want to be automatically redirected to results when search execution completes so that I can begin reviewing findings.

### Natural Language Requirements

- The system shall integrate with Google Search API via Serper using Python `requests` library for search execution
- The system shall execute all queries defined in a search strategy using Celery background tasks
- The system shall provide a Search Execution Status page using Django views showing:
  - Overall progress (queries completed/total) from Django ORM queries
  - Individual query status from `SearchExecution` model
  - Any error messages stored in database fields
  - Estimated completion time calculated in Python
- The system shall handle search execution asynchronously using Celery workers to prevent blocking Django views
- The system shall store raw search results in PostgreSQL using Django ORM as they're retrieved
- The system shall implement basic pagination handling for large result sets in Celery tasks
- The system shall provide error handling for API failures, rate limits, and network issues in Celery tasks
- The system shall update execution status in real-time using JavaScript polling of Django AJAX endpoints
- The system shall automatically transition users to Results Overview when execution completes using Django redirects
- The system shall allow users to cancel ongoing searches using Celery task revocation if needed

---

## Results Processing and Management

### User Stories

**As a researcher**, I want search results to be automatically processed and normalised so that I can work with clean, consistent data.

**As a researcher**, I want to view all my search results in an organised interface so that I can begin reviewing them.

**As a researcher**, I want to filter and sort results so that I can focus on the most relevant items first.

**As a researcher**, I want to see basic metadata for each result so that I can quickly assess relevance.

### Natural Language Requirements

- The system shall automatically process raw search results into normalised format using Celery background tasks
- The system shall perform URL normalisation using Python URL parsing libraries to ensure consistency
- The system shall extract basic metadata using Python libraries including:
  - Domain/source using URL parsing
  - File type using URL analysis and content-type detection
  - Publication indicators using text analysis
- The system shall provide a Results Overview page using Django ListView displaying processed results
- The system shall implement filtering options using Django ORM queries and form filters by:
  - Domain using CharField lookups
  - File type using ChoiceField filters
  - Review status using ForeignKey relationships
  - Date ranges using DateField filters
- The system shall implement sorting options using Django ORM `order_by()` by:
  - Relevance score from search results
  - Date from extracted metadata
  - Source domain alphabetically
  - Review status by tag assignments
- The system shall display result previews using Django templates including title, URL, and snippet
- The system shall handle large result sets using Django Paginator for efficient page loading
- The system shall provide search within results functionality using Django ORM `icontains` lookups
- The system shall maintain traceability to original search queries using ForeignKey relationships

---

## Results Review and Annotation

### User Stories

**As a researcher**, I want to tag results as included, excluded, or maybe so that I can categorise them for my review.

**As a researcher**, I want to provide exclusion reasons when I exclude results so that I can document my decision-making process.

**As a researcher**, I want to add notes to individual results so that I can capture my thoughts and observations.

**As a researcher**, I want to track my review progress so that I know how much work remains.

**As a researcher**, I want to filter results by review status so that I can focus on unreviewed items.

### Natural Language Requirements

- The system shall provide tagging functionality using Django forms with predefined `ReviewTag` options:
  - Include: results that meet inclusion criteria
  - Exclude: results that don't meet criteria
  - Maybe: results requiring further consideration
- The system shall require exclusion reasons using Django form validation when users tag results as "Exclude"
- The system shall provide common exclusion reason options using Django ChoiceField plus TextField for free text
- The system shall allow users to add notes to individual results using Django ModelForm for `Note` model
- The system shall support rich text formatting in notes using Django widget or third-party rich text editor
- The system shall display review progress indicators using Django ORM aggregation showing:
  - Total results count using `Count()` aggregation
  - Reviewed vs unreviewed counts using conditional aggregation
  - Distribution of include/exclude/maybe tags using `Count()` with filters
- The system shall provide filtering by review status using Django ORM filters and form-based filtering
- The system shall save all review actions immediately using Django AJAX views to prevent data loss
- The system shall support bulk operations using Django formsets for efficient reviewing
- The system shall maintain PRISMA-compliant workflow documentation using structured database fields
- The system shall timestamp all review actions using Django model `auto_now` and `auto_now_add` for audit trails

---

## Reporting and Export

### User Stories

**As a researcher**, I want to generate reports showing my search and review statistics so that I can document my methodology.

**As a researcher**, I want to export my results in multiple formats so that I can use them in other tools and publications.

**As a researcher**, I want to see PRISMA flow diagram data so that I can create publication-ready documentation.

**As a researcher**, I want to view summary statistics about my search results so that I can understand the scope of my review.

### Natural Language Requirements

- The system shall provide a Reporting page using Django views accessible from completed sessions
- The system shall generate basic PRISMA flow diagram data using Django ORM aggregation including:
  - Records identified through database searching using `Count()` on search results
  - Records screened using review tag counts
  - Records excluded with reasons using filtered aggregation
  - Full-text articles assessed for eligibility using inclusion tag counts
  - Studies included in review using final inclusion counts
- The system shall display summary statistics using Django ORM queries including:
  - Total results by source using `Count()` with `group_by()`
  - Results by domain/file type using metadata field aggregation
  - Tag distribution (include/exclude/maybe) using `Count()` on tag assignments
  - Review completion percentage using calculated fields
- The system shall support export in multiple formats using Python libraries:
  - CSV: using Python `csv` module for data analysis
  - JSON: using Python `json` module for programmatic use
  - Basic PDF: using `ReportLab` or `WeasyPrint` for documentation
- The system shall include all relevant metadata in exports using Django ORM `select_related()` and `prefetch_related()`
- The system shall allow users to select which data to include in exports using Django forms with checkboxes
- The system shall provide export of both full results and filtered subsets using Django ORM filtering
- The system shall generate exports efficiently using Django streaming responses for large datasets
- The system shall maintain data integrity and formatting in all export formats using proper serialisation

---

## System Architecture and Performance

### User Stories

**As a user**, I want the application to respond quickly so that I can work efficiently.

**As a user**, I want my data to be saved reliably so that I don't lose my work.

**As a developer**, I want the code to be well-organised so that I can maintain and extend it easily.

### Natural Language Requirements

- The system shall follow Django app-based modular architecture principles for maintainability
- The system shall use PostgreSQL database with proper indexing using Django `db_index=True` for performance
- The system shall implement proper error handling and logging using Django logging framework throughout
- The system shall provide loading indicators for long-running operations using JavaScript with Django AJAX views
- The system shall use Django ORM with proper query optimisation using `select_related()` and `prefetch_related()`
- The system shall implement proper data validation using Django form validation on both client and server
- The system shall use Django templates with template inheritance for efficient UI rendering
- The system shall implement proper state management using Django sessions and database persistence
- The system shall provide responsive design using CSS (potentially TailwindCSS) for various screen sizes
- The system shall implement proper security measures using Django's built-in security features including:
  - Input sanitisation using Django form cleaning
  - SQL injection prevention using Django ORM parameterised queries
  - XSS protection using Django template auto-escaping
  - CSRF protection using Django CSRF middleware
- The system shall handle concurrent user operations safely using Django database transactions
- The system shall provide proper backup and recovery mechanisms using PostgreSQL backup tools

---

## Acceptance Criteria Templates

### For Authentication Stories:
- [ ] User can successfully register using Django UserCreationForm with valid credentials
- [ ] User receives appropriate error messages for invalid inputs via Django form validation
- [ ] User can log in with correct credentials using Django AuthenticationForm
- [ ] User is redirected to Review Manager dashboard after successful login
- [ ] User cannot access protected pages without authentication (Django login_required)
- [ ] User can update profile information successfully using Django ModelForm

### For Search Strategy Stories:
- [ ] User can create new search strategies using Django ModelForm
- [ ] User can organise concepts using PIC framework with proper form fields
- [ ] User can select domains and file types using Django ChoiceField
- [ ] User can see real-time query preview using JavaScript and Django AJAX
- [ ] User can save and modify strategies using Django ORM
- [ ] Form validation works correctly using Django form validation

### For Search Execution Stories:
- [ ] Searches execute successfully with Serper API integration using Celery tasks
- [ ] Progress is tracked and displayed accurately using Django ORM and AJAX polling
- [ ] Errors are handled gracefully with clear messages stored in database
- [ ] Results are stored correctly in PostgreSQL using Django ORM
- [ ] User is redirected to results when complete using Django URL routing

### For Results Review Stories:
- [ ] Results display correctly with all metadata using Django templates and ORM
- [ ] Filtering and sorting work as expected using Django ORM queries
- [ ] Tagging functionality works correctly using Django forms and models
- [ ] Notes can be added and saved using Django ModelForm
- [ ] Progress tracking is accurate using Django ORM aggregation
- [ ] Bulk operations work efficiently using Django formsets

### For Reporting Stories:
- [ ] Reports generate correctly with accurate data using Django ORM aggregation
- [ ] Exports work in all specified formats using Python libraries
- [ ] PRISMA data is calculated correctly using Django ORM queries
- [ ] Summary statistics are accurate using proper aggregation
- [ ] Export files contain expected data structure with proper serialisation

---

## Technical Implementation Notes

### Django-Specific Considerations:

#### Database and ORM:
- Implement proper indexing using `db_index=True` on frequently queried fields
- Use Django migrations for all schema changes
- Optimise queries with `select_related()` and `prefetch_related()`
- Consider read replicas for reporting queries in production

#### Background Tasks:
- Configure Celery with Redis or RabbitMQ as message broker
- Implement proper task monitoring and error handling
- Use Celery beat for scheduled tasks if needed
- Monitor task queue performance and scaling

#### API Integration:
- Store API keys in Django settings using environment variables
- Implement proper rate limiting using Django cache framework
- Add retry logic for failed requests in Celery tasks
- Monitor API usage and costs through logging

#### Performance Optimisation:
- Use Django Paginator for large result sets
- Implement Django cache framework for frequently accessed data
- Optimise template rendering with proper template inheritance
- Use Django's static file handling for CSS/JS assets

#### Security Measures:
- Validate all inputs using Django form validation
- Use Django's built-in CSRF and XSS protection
- Implement proper session management using Django sessions
- Use HTTPS in production with proper SSL configuration
- Regular security updates using Django's security framework

#### Testing Strategy:
- Write unit tests using Django TestCase
- Implement integration tests for full workflows
- Use Django's test client for view testing
- Test Celery tasks using appropriate test frameworks
- Implement continuous integration with GitHub Actions

#### Deployment Considerations:
- Use Docker for containerisation with proper Django configuration
- Configure Gunicorn/Uvicorn for production WSGI/ASGI serving
- Set up Nginx for static file serving and reverse proxy
- Implement proper logging and monitoring in production
- Use Django's deployment checklist for security configuration