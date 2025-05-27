# User Story: User Logout

**ID:** AUTH-003
**Title:** User Logout
**As a:** Logged-in Researcher
**I want to:** Log out of the Thesis Grey application
**So that I can:** Securely end my session and prevent unauthorized access to my account.

---

## Description

This story covers the functionality for a logged-in user to securely log out of the Thesis Grey platform, terminating their current session.

**Depends On:** AUTH-002 (User Login)

---

## Acceptance Criteria

1.  **AC1: Logout Link/Button Availability:**
    *   **Given** a user is logged in
    *   **When** they are on any authenticated page of the application
    *   **Then** a clear link or button to "Log Out" or "Sign Out" is visible and accessible (e.g., in a user menu or navigation bar).
2.  **AC2: Successful Logout:**
    *   **Given** a user is logged in
    *   **When** they click the "Log Out" link/button
    *   **Then** their current session is terminated.
    *   **And** they are redirected to the login page or a public landing page (e.g., homepage).
    *   **And** a confirmation message (e.g., "You have been successfully logged out.") may be displayed.
3.  **AC3: Access Restriction After Logout:**
    *   **Given** a user has successfully logged out
    *   **When** they attempt to access any page that requires authentication (e.g., Review Manager Dashboard, specific search session)
    *   **Then** they are redirected to the login page.
    *   **And** they are prompted to log in.
4.  **AC4: No Logout Option for Unauthenticated Users:**
    *   **Given** a user is not logged in
    *   **When** they are on a public page of the application
    *   **Then** the "Log Out" link/button is not visible or is disabled.

---

## Technical Notes (from ARCHITECTURE.md & PRD-D.md)

*   To be implemented within the `accounts` Django app.
*   Utilizes Django's built-in `LogoutView`.
*   Templates: No specific new template is typically required for logout itself, but the redirection target (e.g., login page) should exist.
*   Session termination handled by Django.

---

## Out of Scope for this Story

*   Automatic session timeout.

---

## Open Questions/Assumptions

*   **Assumption:** Redirection to the login page after logout is the desired behavior.

---

**Priority:** High (Essential for security and session management)
**Effort Estimate (Story Points):** TBD (e.g., 1-2 points)