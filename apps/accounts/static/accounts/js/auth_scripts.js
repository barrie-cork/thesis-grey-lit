// apps/accounts/static/accounts/js/auth_scripts.js

document.addEventListener('DOMContentLoaded', function() {
    const eyeIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">
        <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.659-2.94C4.086 3.29 6.015 2.5 8 2.5c1.985 0 3.914.79 5.168 2.56C14.167 6.06 14.827 8 14.827 8s-.66 1.94-1.828 3.44C11.914 13.21 9.985 14 8 14c-1.985 0-3.914-.79-5.168-2.56A13.133 13.133 0 0 1 1.172 8z"/>
        <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>
    </svg>`;
    const eyeSlashIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">
        <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>
        <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.288.822.822.073.073.026.026a3.5 3.5 0 0 0 4.474 4.474l.823.823a2.5 2.5 0 0 1-2.829-2.829l-.822-.822-.073-.073-.026-.026z"/>
        <path d="M2.36 1.358A2.062 2.062 0 0 0 .068 3.312l1.758 1.758L1.101 6.43A13.132 13.132 0 0 0 1.172 8l.001.002.002.001.005.006c.064.131.14.27.224.408.09.145.187.298.29.455.283.424.628.905 1.048 1.403l.157.191.049.058.041.045.008.008c.058.052.12.1.188.147a1.04 1.04 0 0 0 .19.139l.372.264.001.001.001.001.001.001a.07.07 0 0 1 .003.002l.004.002.005.003.007.003.004.002a15.628 15.628 0 0 0 2.004.86l.759.29.055.02a1.74 1.74 0 0 0 .42.118.98.98 0 0 0 .43.075c.063.003.125.003.187.003a2.066 2.066 0 0 0 .364-.04l1.758 1.758a2.062 2.062 0 0 0 2.953-2.953L2.36 1.358zM1.013 7.978A13.134 13.134 0 0 1 8 2.5c.548 0 1.08.043 1.603.128L5.74 5.74a3.486 3.486 0 0 0-.577.98A3.484 3.484 0 0 0 4.5 8a3.488 3.488 0 0 0 .61 1.952l-2.692 2.692A13.133 13.133 0 0 1 1.013 7.978z"/>
        <path d="M8.001 9.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
    </svg>`;

    document.querySelectorAll('button[id^="togglePasswordVisibility"]').forEach(button => {
        button.addEventListener('click', function() {
            const passwordField = this.previousElementSibling;
            if (passwordField && passwordField.type === 'password') {
                passwordField.type = 'text';
                this.innerHTML = eyeSlashIconSvg;
            } else if (passwordField) {
                passwordField.type = 'password';
                this.innerHTML = eyeIconSvg;
            }
        });
    });

    // Auto-focus on the first visible input field in a form, that is not a button or hidden input
    const form = document.querySelector('.card-body form');
    if (form) {
        const firstInput = form.querySelector('input:not([type="hidden"]):not([type="button"]):not([type="submit"]):not([type="reset"]), select, textarea');
        if (firstInput) {
            firstInput.focus();
        }
    }

    // Password strength meter
    const passwordField = document.getElementById('id_password1'); // Default ID for UserCreationForm password1
    const strengthIndicator = document.getElementById('password-strength-indicator');
    const strengthText = document.getElementById('password-strength-text');

    if (passwordField && strengthIndicator && strengthText) {
        passwordField.addEventListener('input', function() {
            const password = this.value;
            let score = 0;
            let strengthLabel = '';
            let strengthClass = '';

            if (password.length === 0) {
                score = -1; // Special case for empty
            } else {
                if (password.length >= 8) score++;
                if (password.length >= 12) score++;
                if (/[A-Z]/.test(password)) score++;
                if (/[a-z]/.test(password)) score++;
                if (/[0-9]/.test(password)) score++;
                if (/[^A-Za-z0-9]/.test(password)) score++;
            }

            switch (score) {
                case -1: // Empty
                    strengthLabel = '';
                    strengthClass = '';
                    break;
                case 0:
                case 1:
                case 2:
                    strengthLabel = 'Weak';
                    strengthClass = 'weak';
                    break;
                case 3:
                    strengthLabel = 'Medium';
                    strengthClass = 'medium';
                    break;
                case 4:
                case 5:
                    strengthLabel = 'Strong';
                    strengthClass = 'strong';
                    break;
                case 6:
                    strengthLabel = 'Very Strong';
                    strengthClass = 'very-strong';
                    break;
                default:
                    strengthLabel = 'Weak';
                    strengthClass = 'weak';
            }
            
            strengthIndicator.className = 'mt-1 '; // Reset classes, keep mt-1
            if (strengthClass) {
                strengthIndicator.classList.add(strengthClass);
            }
            strengthText.textContent = strengthLabel;
            strengthText.className = 'mt-1 '; // Reset classes, keep mt-1
            if (strengthClass) {
                 strengthText.classList.add(strengthClass);
            }
        });
    }

    // Form submission loading state for auth cards
    const authForms = document.querySelectorAll('.auth-card form');
    authForms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            }
        });
    });

}); 