# User Story: Basic Profile Viewing

**ID:** AUTH-004
**Title:** Basic Profile Viewing
**As a:** Logged-in Researcher
**I want to:** View my basic profile information
**So that I can:** Confirm my account details (e.g., username, email).

---

## Description

This story covers the functionality for a logged-in user to view their basic profile information. For Phase 1, this will be a very simple display of non-editable core details.

**Depends On:** AUTH-002 (User Login)

---

## Acceptance Criteria

1.  **AC1: Profile Page Access:**
    *   **Given** a user is logged in
    *   **When** they navigate to a "Profile" or "My Account" section (e.g., via a user menu)
    *   **Then** they are taken to their profile page.
2.  **AC2: Display Basic Information:**
    *   **Given** the user is on their profile page
    *   **When** the page loads
    *   **Then** at least the following information is displayed:
        *   Username
        *   Email address
        *   (Optional for Phase 1 display: First Name, Last Name, Date Joined - if available on User model)
3.  **AC3: Information is Read-Only (Phase 1):**
    *   **Given** the user is viewing their profile page
    *   **Then** the displayed information is read-only; no editing functionality is available in this story.

---

## Technical Notes (from ARCHITECTURE.md & PRD-D.md)

*   To be implemented within the `accounts` Django app.
*   Views: Custom view (e.g., `UserProfileView` as a `DetailView` or `TemplateView`) to fetch and display the `request.user` object's details.
*   Templates: Custom HTML template for the profile page (`profile.html`).
*   User Model: Displays fields from Django's built-in `User` model or the custom `AbstractUser` if implemented.

---

## Out of Scope for this Story

*   Editing profile information (this will be a separate, future story).
*   Changing password (this will be a separate, future story).
*   Uploading a profile picture.
*   Displaying activity logs or other advanced profile details.

---

## Open Questions/Assumptions

*   **Assumption:** For Phase 1, displaying username and email is the minimum. Displaying `first_name`, `last_name`, `date_joined` is a "nice-to-have" if easily available from the user model.
*   **Assumption:** No profile editing is required for this initial story.

---

**Priority:** Medium (Lower than core login/registration/logout, but good for basic account verification)
**Effort Estimate (Story Points):** TBD (e.g., 1-2 points)