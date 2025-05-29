// Review Manager Dashboard JavaScript

class ReviewManagerDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.initializeEventListeners();
        this.initializeSearch();
        this.initializeTooltips();
        this.initializeCardInteractions();
    }

    initializeEventListeners() {
        // Search functionality
        const searchInput = document.querySelector('.search-box input');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });
        }

        // Status filter
        const statusFilter = document.querySelector('.status-filter select');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.applyStatusFilter(e.target.value);
            });
        }

        // Clear filters
        const clearFiltersBtn = document.querySelector('.btn-link');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.clearFilters();
            });
        }
    }

    initializeSearch() {
        // Real-time search without page reload
        this.searchCache = new Map();
    }

    performSearch(query) {
        const cards = document.querySelectorAll('.session-card');
        const trimmedQuery = query.toLowerCase().trim();

        cards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const description = card.querySelector('p').textContent.toLowerCase();
            
            const matches = trimmedQuery === '' || 
                           title.includes(trimmedQuery) || 
                           description.includes(trimmedQuery);
            
            if (matches) {
                card.style.display = '';
                card.classList.remove('hidden');
            } else {
                card.style.display = 'none';
                card.classList.add('hidden');
            }
        });

        this.updateResultsCount();
    }

    applyStatusFilter(status) {
        const cards = document.querySelectorAll('.session-card');
        
        cards.forEach(card => {
            const cardStatus = card.dataset.status;
            
            if (status === 'all' || status === cardStatus || 
                (status === 'active' && !['completed', 'archived', 'failed'].includes(cardStatus))) {
                card.style.display = '';
                card.classList.remove('filtered-out');
            } else {
                card.style.display = 'none';
                card.classList.add('filtered-out');
            }
        });

        this.updateResultsCount();
    }

    clearFilters() {
        // Clear search input
        const searchInput = document.querySelector('.search-box input');
        if (searchInput) {
            searchInput.value = '';
        }

        // Reset status filter
        const statusFilter = document.querySelector('.status-filter select');
        if (statusFilter) {
            statusFilter.value = 'all';
        }

        // Show all cards
        const cards = document.querySelectorAll('.session-card');
        cards.forEach(card => {
            card.style.display = '';
            card.classList.remove('hidden', 'filtered-out');
        });

        this.updateResultsCount();
        
        // Update URL without filters
        window.history.replaceState({}, '', window.location.pathname);
    }

    updateResultsCount() {
        const visibleCards = document.querySelectorAll('.session-card:not([style*="display: none"])');
        const totalCards = document.querySelectorAll('.session-card');
        
        // Update any results counter if it exists
        const resultsCounter = document.querySelector('.results-counter');
        if (resultsCounter) {
            resultsCounter.textContent = `Showing ${visibleCards.length} of ${totalCards.length} sessions`;
        }

        // Show/hide empty state
        this.toggleEmptyState(visibleCards.length === 0 && totalCards.length > 0);
    }

    toggleEmptyState(show) {
        let emptyState = document.querySelector('.no-results-state');
        
        if (show && !emptyState) {
            emptyState = document.createElement('div');
            emptyState.className = 'no-results-state empty-state';
            emptyState.innerHTML = `
                <h3>No sessions found</h3>
                <p>Try adjusting your search criteria or filters.</p>
                <button type="button" class="btn btn-outline-secondary" onclick="reviewManagerDashboard.clearFilters()">
                    Clear Filters
                </button>
            `;
            document.querySelector('.sessions-grid').appendChild(emptyState);
        } else if (!show && emptyState) {
            emptyState.remove();
        }
    }

    initializeTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    initializeCardInteractions() {
        const cards = document.querySelectorAll('.session-card');
        
        cards.forEach(card => {
            // Make cards keyboard accessible
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            
            // Add click handler for navigation
            card.addEventListener('click', (e) => {
                // Don't navigate if clicking on action buttons
                if (e.target.closest('.action-btn')) {
                    return;
                }
                
                const sessionId = card.dataset.sessionId;
                if (sessionId) {
                    this.navigateToSession(sessionId);
                }
            });

            // Add keyboard navigation
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    card.click();
                }
            });

            // Add hover effects
            card.addEventListener('mouseenter', () => {
                this.highlightCard(card);
            });

            card.addEventListener('mouseleave', () => {
                this.unhighlightCard(card);
            });
        });
    }

    navigateToSession(sessionId) {
        // Add loading state
        const card = document.querySelector(`[data-session-id="${sessionId}"]`);
        if (card) {
            card.classList.add('loading');
        }

        // Navigate to session (this would be set up in the template)
        const nextUrl = card.dataset.nextUrl;
        if (nextUrl) {
            window.location.href = nextUrl;
        }
    }

    highlightCard(card) {
        card.style.transform = 'translateY(-2px)';
        card.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
    }

    unhighlightCard(card) {
        if (!card.classList.contains('loading')) {
            card.style.transform = '';
            card.style.boxShadow = '';
        }
    }

    // Utility method for AJAX requests if needed
    async makeRequest(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Request failed:', error);
            this.showError('An error occurred. Please try again.');
            throw error;
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    showError(message) {
        // Create error alert if one doesn't exist
        const existingAlert = document.querySelector('.alert-danger');
        if (existingAlert) {
            existingAlert.remove();
        }

        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.container');
        container.insertBefore(alert, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    showSuccess(message) {
        // Create success alert
        const existingAlert = document.querySelector('.alert-success');
        if (existingAlert) {
            existingAlert.remove();
        }

        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.container');
        container.insertBefore(alert, container.firstChild);

        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 3000);
    }
}

// Initialize dashboard when DOM is loaded
let reviewManagerDashboard;

document.addEventListener('DOMContentLoaded', function() {
    reviewManagerDashboard = new ReviewManagerDashboard();
});

// Export for use in other scripts if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ReviewManagerDashboard;
}
