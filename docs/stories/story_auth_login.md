# User Story: User Login

**ID:** AUTH-002
**Title:** User Login
**As a:** Registered Researcher
**I want to:** Log in to the Thesis Grey application using my credentials
**So that I can:** Access my search sessions and continue my work.

---

## Description

This story covers the functionality for an existing registered user to log in to the Thesis Grey platform. The login process should verify the user's credentials (username and password) against the stored records.

**Depends On:** AUTH-001 (User Registration)

---

## Acceptance Criteria

1.  **AC1: Login Form Availability:**
    *   **Given** a user is not logged in
    *   **When** they navigate to the application
    *   **Then** a clear link or button to "Log In" or "Sign In" is visible.
2.  **AC2: Login Form Fields:**
    *   **Given** the user clicks on the "Log In" link/button
    *   **When** the login page loads
    *   **Then** a form is presented requesting:
        *   Username
        *   Password
3.  **AC3: Successful Login:**
    *   **Given** a registered user enters their correct username and password
    *   **When** they submit the login form
    *   **Then** their credentials are validated against the system.
    *   **And** a new session is created for the user.
    *   **And** they are redirected to the Review Manager Dashboard.
4.  **AC4: Invalid Credentials (Username or Password):**
    *   **Given** a user enters an incorrect username or password
    *   **When** they submit the login form
    *   **Then** an informative error message is displayed (e.g., "Invalid username or password.").
    *   **And** the user is not logged in.
    *   **And** they remain on the login page (or are returned to it).
5.  **AC5: Required Fields Validation:**
    *   **Given** a user attempts to submit the login form without filling in the username or password
    *   **When** they submit the form
    *   **Then** informative error messages are displayed next to the respective empty required fields.
    *   **And** the user is not logged in.
6.  **AC6: Already Logged In:**
    *   **Given** a user is already logged in
    *   **When** they attempt to navigate to the login page
    *   **Then** they are redirected to the Review Manager Dashboard (or another appropriate authenticated page).

---

## Technical Notes (from ARCHITECTURE.md & PRD-D.md)

*   To be implemented within the `accounts` Django app.
*   Utilizes Django's built-in `AuthenticationForm`.
*   Views: Django's built-in `LoginView`.
*   Templates: Custom HTML template for the login page (`login.html`).
*   Session management handled by Django.

---

## Out of Scope for this Story

*   "Remember Me" functionality.
*   "Forgot Password" functionality.
*   Login attempt throttling or lockout mechanisms (can be a separate security enhancement story).

---

## Open Questions/Assumptions

*   **Assumption:** Standard username/password login is sufficient for Phase 1.

---

**Priority:** High (Fundamental for user access)
**Effort Estimate (Story Points):** TBD (e.g., 2-3 points)