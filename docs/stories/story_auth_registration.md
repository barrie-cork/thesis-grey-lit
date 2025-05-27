# User Story: User Registration

**ID:** AUTH-001
**Title:** User Registration
**As a:** New Researcher
**I want to:** Create a new account in the Thesis Grey application
**So that I can:** Access its features to manage and review grey literature for my research.
**Status:** InProgress

---

## Description

This story covers the functionality for a new user to register for an account on the Thesis Grey platform. The registration process should collect necessary information (e.g., username, email, password) and create a new user record in the system.

**Depends On:** N/A (Initial feature)

---

## Acceptance Criteria

1.  **AC1: Registration Form Availability:**
    *   **Given** a user is not logged in
    *   **When** they navigate to the application
    *   **Then** a clear link or button to "Register" or "Sign Up" is visible.
2.  **AC2: Registration Form Fields:**
    *   **Given** the user clicks on the "Register" link/button
    *   **When** the registration page loads
    *   **Then** a form is presented requesting at least:
        *   Username (must be unique)
        *   Email address (must be unique and valid format)
        *   Password
        *   Password confirmation
3.  **AC3: Successful Registration:**
    *   **Given** the user fills in all required fields with valid and unique information
    *   **And** the password and password confirmation match
    *   **When** they submit the registration form
    *   **Then** a new user account is created in the system.
    *   **And** their password is securely hashed and stored.
    *   **And** the user is automatically logged in (or redirected to the login page with a success message).
    *   **And** they are redirected to the Review Manager Dashboard (or a welcome page).
4.  **AC4: Username Already Exists:**
    *   **Given** a user attempts to register with a username that already exists
    *   **When** they submit the registration form
    *   **Then** an informative error message is displayed indicating the username is taken.
    *   **And** the user is not registered.
5.  **AC5: Email Already Exists:**
    *   **Given** a user attempts to register with an email address that already exists
    *   **When** they submit the registration form
    *   **Then** an informative error message is displayed indicating the email is already in use.
    *   **And** the user is not registered.
6.  **AC6: Invalid Email Format:**
    *   **Given** a user enters an email address in an invalid format
    *   **When** they submit the registration form
    *   **Then** an informative error message is displayed indicating the email format is invalid.
    *   **And** the user is not registered.
7.  **AC7: Password Mismatch:**
    *   **Given** a user enters a password and password confirmation that do not match
    *   **When** they submit the registration form
    *   **Then** an informative error message is displayed indicating the passwords do not match.
    *   **And** the user is not registered.
8.  **AC8: Weak Password (Optional - for consideration):**
    *   **Given** a user enters a password that does not meet minimum complexity requirements (e.g., length, character types - if defined)
    *   **When** they submit the registration form
    *   **Then** an informative error message is displayed indicating the password requirements.
    *   **And** the user is not registered.
        *   *Note: Minimum complexity rules to be defined if this AC is prioritized.*
9.  **AC9: Required Fields Validation:**
    *   **Given** a user attempts to submit the registration form without filling all required fields
    *   **When** they submit the form
    *   **Then** informative error messages are displayed next to the respective empty required fields.
    *   **And** the user is not registered.

---

## Technical Notes (from ARCHITECTURE.md & PRD-D.md)

*   To be implemented within the `accounts` Django app.
*   Utilizes Django's built-in `UserCreationForm` as a base, potentially customized.
*   Views: Custom view for signup.
*   Templates: Custom HTML template for the registration page (`signup.html`).
*   User Model: Django's built-in `User` model, or a custom model inheriting from `AbstractUser` if additional fields (e.g., `first_name`, `last_name` beyond username/email) are deemed necessary for profile at registration. PRD Section 4.1 suggests this possibility.
*   Password hashing and session management handled by Django.

---

## Out of Scope for this Story

*   Email verification process post-registration.
*   Social login (e.g., Google, GitHub).
*   "Forgot Password" functionality.
*   Advanced profile field collection beyond basic registration.

---

## Open Questions/Assumptions

*   **Assumption:** For Phase 1, basic registration (username, email, password) is sufficient. `first_name` and `last_name` can be optional or part of a separate profile update story.
*   **Question:** Are there specific password complexity rules to enforce for Phase 1, or is Django's default handling sufficient? (Affects AC8)

---

**Priority:** High (Fundamental for user access)
**Effort Estimate (Story Points):** TBD (e.g., 3-5 points, depending on complexity of form and views)

---

## Implementation Notes & Log

*   **2025-05-26 22:59:** Full Stack Dev (James) activated. Story status updated to `InProgress`.
*   **2025-05-26 22:59:** Starting review of essential context documents as per Dev Agent S.O.P. 1.3.
    *   Assigned Story File ([`docs/stories/story_auth_registration.md`](docs/stories/story_auth_registration.md:1)): Reviewed.
    *   `Project Structure` ([`docs/project-structure.md`](docs/project-structure.md:21)): Created and reviewed.
    *   `Operational Guidelines` ([`docs/operational-guidelines.md`](docs/operational-guidelines.md:22)): Created and reviewed.
    *   `Technology Stack` ([`docs/tech-stack.md`](docs/tech-stack.md:23)): Attempted to read, file not found. This is a blocker.