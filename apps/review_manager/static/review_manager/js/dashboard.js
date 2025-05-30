// Review Manager Dashboard JavaScript - Enhanced for Sprint 5

class ReviewManagerDashboard {
    constructor() {
        this.contextualHelp = new ContextualHelpManager();
        this.breadcrumbs = new BreadcrumbManager();
        this.init();
    }

    init() {
        this.initializeEventListeners();
        this.initializeSearch();
        this.initializeTooltips();
        this.initializeCardInteractions();
        this.initializeContextualHelp();
        this.initializeBreadcrumbs();
        this.initializeKeyboardShortcuts();
        this.initializePerformanceMonitoring();
    }

    initializeEventListeners() {
        // Enhanced search functionality with debouncing
        const searchInput = document.querySelector('#searchInput');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                
                // Show loading indicator
                this.showSearchLoading(true);
                
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                    this.showSearchLoading(false);
                }, 300);
            });
        }

        // Enhanced filter handling
        const statusFilter = document.querySelector('#statusFilter');
        const dateFilter = document.querySelector('#dateFilter');
        const sortFilter = document.querySelector('#sortFilter');
        
        [statusFilter, dateFilter, sortFilter].forEach(filter => {
            if (filter) {
                filter.addEventListener('change', (e) => {
                    this.applyFilters();
                    this.saveFilterState();
                });
            }
        });

        // Quick filter chips
        const quickFilters = document.querySelectorAll('.quick-filter');
        quickFilters.forEach(filter => {
            filter.addEventListener('click', (e) => {
                e.preventDefault();
                this.applyQuickFilter(filter.dataset.status);
            });
        });

        // Clear filters
        const clearFiltersBtn = document.querySelector('.clear-filters a');
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
                // Don't navigate if clicking on action buttons or dropdowns
                if (e.target.closest('.action-btn, .dropdown, .btn')) {
                    return;
                }
                
                const nextUrl = card.dataset.nextUrl;
                if (nextUrl) {
                    this.navigateToSession(card, nextUrl);
                }
            });

            // Add keyboard navigation
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    card.click();
                }
            });

            // Add hover effects with performance optimization
            let hoverTimeout;
            card.addEventListener('mouseenter', () => {
                clearTimeout(hoverTimeout);
                hoverTimeout = setTimeout(() => {
                    this.highlightCard(card);
                }, 50);
            });

            card.addEventListener('mouseleave', () => {
                clearTimeout(hoverTimeout);
                this.unhighlightCard(card);
            });
        });
    }

    navigateToSession(card, url) {
        // Add loading state
        card.classList.add('loading');
        
        // Add navigation tracking
        this.trackNavigation(card.dataset.sessionId, card.dataset.status);
        
        // Navigate
        window.location.href = url;
    }

    trackNavigation(sessionId, status) {
        // Track user navigation patterns for UX improvements
        console.log('Navigation:', { sessionId, status, timestamp: new Date().toISOString() });
    }

    highlightCard(card) {
        if (!card.classList.contains('loading')) {
            card.style.transform = 'translateY(-4px)';
            card.style.transition = 'all 0.2s ease';
        }
    }

    unhighlightCard(card) {
        if (!card.classList.contains('loading')) {
            card.style.transform = '';
        }
    }

    // Utility methods
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
        this.showMessage(message, 'danger');
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showInfo(message) {
        this.showMessage(message, 'info');
    }

    showMessage(message, type = 'info') {
        // Remove existing alerts of the same type
        const existingAlert = document.querySelector(`.alert-${type}`);
        if (existingAlert) {
            existingAlert.remove();
        }

        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        const container = document.querySelector('.dashboard-container');
        container.insertBefore(alert, container.firstChild);

        // Auto-dismiss based on type
        const dismissTime = type === 'success' ? 3000 : type === 'danger' ? 7000 : 5000;
        setTimeout(() => {
            if (alert.parentNode) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 150);
            }
        }, dismissTime);
    }
}

// Sprint 5 Task 27: Contextual Help Manager
class ContextualHelpManager {
    constructor() {
        this.helpData = {
            dashboard: {
                title: 'Dashboard Help',
                content: 'Manage all your literature review sessions from this central dashboard.',
                tips: [
                    'Use the search box to quickly find sessions',
                    'Filter by status to see specific types of sessions',
                    'Click on session cards to continue where you left off',
                    'Use keyboard shortcuts: Ctrl+F to search, Ctrl+N for new session'
                ]
            },
            filters: {
                title: 'Advanced Filtering',
                content: 'Use multiple filters to find exactly what you\'re looking for.',
                tips: [
                    'Combine search with status filters for precise results',
                    'Date filters help find recent or older sessions',
                    'Quick filter chips provide one-click access to common filters',
                    'Your filter preferences are automatically saved'
                ]
            },
            sessionCard: {
                title: 'Session Cards',
                content: 'Each card shows your session\'s current status and next steps.',
                tips: [
                    'Status badges show where your session is in the workflow',
                    'Click the main action button to continue your work',
                    'Use the dropdown menu for additional actions',
                    'Cards are ordered by priority and recent activity'
                ]
            }
        };
        this.currentHelp = null;
    }

    init() {
        this.createHelpButton();
        this.initializeTooltips();
        this.addHelpTriggers();
    }

    createHelpButton() {
        const helpButton = document.createElement('button');
        helpButton.className = 'btn btn-outline-info btn-sm help-toggle';
        helpButton.innerHTML = '<i>❓</i> Help';
        helpButton.style.position = 'fixed';
        helpButton.style.bottom = '20px';
        helpButton.style.right = '20px';
        helpButton.style.zIndex = '1000';
        helpButton.setAttribute('data-bs-toggle', 'tooltip');
        helpButton.setAttribute('title', 'Get contextual help');
        
        helpButton.addEventListener('click', () => {
            this.toggleHelp();
        });
        
        document.body.appendChild(helpButton);
    }

    initializeTooltips() {
        // Add contextual tooltips to various elements
        const tooltips = [
            { selector: '.search-box input', title: 'Search sessions by title or description. Use keywords for best results.' },
            { selector: '#statusFilter', title: 'Filter sessions by their current workflow status.' },
            { selector: '#dateFilter', title: 'Filter sessions by when they were created.' },
            { selector: '#sortFilter', title: 'Change how sessions are ordered in the grid.' },
            { selector: '.quick-filter', title: 'Click for instant filtering by this status type.' },
            { selector: '.status-badge', title: 'Shows current workflow stage. Click for more details.' },
            { selector: '.action-btn', title: 'Primary action to continue your workflow.' }
        ];

        tooltips.forEach(({ selector, title }) => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                element.setAttribute('data-bs-toggle', 'tooltip');
                element.setAttribute('title', title);
            });
        });
    }

    addHelpTriggers() {
        // Add help icons to section headers
        const sections = [
            { selector: '.filters-section', topic: 'filters' },
            { selector: '.sessions-grid', topic: 'sessionCard' }
        ];

        sections.forEach(({ selector, topic }) => {
            const section = document.querySelector(selector);
            if (section) {
                const helpIcon = document.createElement('span');
                helpIcon.className = 'help-icon';
                helpIcon.innerHTML = ' <i style="cursor: help; color: #17a2b8;">ℹ️</i>';
                helpIcon.addEventListener('click', () => {
                    this.showHelp(topic);
                });
                
                // Add to section header or create one
                const header = section.querySelector('h2, h3') || section;
                if (header.tagName && header.tagName.match(/^H[1-6]$/)) {
                    header.appendChild(helpIcon);
                }
            }
        });
    }

    toggleHelp() {
        if (this.currentHelp) {
            this.hideHelp();
        } else {
            this.showHelp('dashboard');
        }
    }

    showHelp(topic) {
        this.hideHelp(); // Close any existing help
        
        const helpData = this.helpData[topic];
        if (!helpData) return;

        const helpPanel = document.createElement('div');
        helpPanel.className = 'help-panel';
        helpPanel.innerHTML = `
            <div class="help-panel-content">
                <div class="help-header">
                    <h5>${helpData.title}</h5>
                    <button type="button" class="btn-close help-close" aria-label="Close"></button>
                </div>
                <div class="help-body">
                    <p>${helpData.content}</p>
                    <h6>Tips:</h6>
                    <ul>
                        ${helpData.tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;

        // Style the help panel
        Object.assign(helpPanel.style, {
            position: 'fixed',
            top: '50%',
            right: '20px',
            transform: 'translateY(-50%)',
            width: '300px',
            maxHeight: '400px',
            backgroundColor: 'white',
            border: '1px solid #dee2e6',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: '1050',
            padding: '0',
            overflow: 'hidden'
        });

        // Style the content
        const content = helpPanel.querySelector('.help-panel-content');
        Object.assign(content.style, {
            padding: '1rem',
            maxHeight: '400px',
            overflowY: 'auto'
        });

        // Style the header
        const header = helpPanel.querySelector('.help-header');
        Object.assign(header.style, {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1rem',
            paddingBottom: '0.5rem',
            borderBottom: '1px solid #dee2e6'
        });

        document.body.appendChild(helpPanel);
        this.currentHelp = helpPanel;

        // Add close event
        helpPanel.querySelector('.help-close').addEventListener('click', () => {
            this.hideHelp();
        });

        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', this.outsideClickHandler.bind(this));
        }, 100);
    }

    hideHelp() {
        if (this.currentHelp) {
            this.currentHelp.remove();
            this.currentHelp = null;
            document.removeEventListener('click', this.outsideClickHandler.bind(this));
        }
    }

    outsideClickHandler(e) {
        if (this.currentHelp && !this.currentHelp.contains(e.target) && 
            !e.target.closest('.help-toggle, .help-icon')) {
            this.hideHelp();
        }
    }
}

// Sprint 5 Task 28: Breadcrumb Manager
class BreadcrumbManager {
    constructor() {
        this.breadcrumbs = [
            { name: 'Dashboard', url: '/review/', active: true }
        ];
    }

    init() {
        this.createBreadcrumbNav();
        this.updateBreadcrumbs();
    }

    createBreadcrumbNav() {
        const existingBreadcrumb = document.querySelector('.breadcrumb-nav');
        if (existingBreadcrumb) return;

        const breadcrumbNav = document.createElement('nav');
        breadcrumbNav.className = 'breadcrumb-nav';
        breadcrumbNav.setAttribute('aria-label', 'breadcrumb');
        
        const breadcrumbList = document.createElement('ol');
        breadcrumbList.className = 'breadcrumb';
        
        breadcrumbNav.appendChild(breadcrumbList);
        
        // Insert after header, before filters
        const header = document.querySelector('.dashboard-header');
        const filters = document.querySelector('.filters-section');
        
        if (header && filters) {
            header.parentNode.insertBefore(breadcrumbNav, filters);
        } else if (header) {
            header.insertAdjacentElement('afterend', breadcrumbNav);
        }
    }

    updateBreadcrumbs() {
        const breadcrumbList = document.querySelector('.breadcrumb');
        if (!breadcrumbList) return;

        breadcrumbList.innerHTML = '';
        
        this.breadcrumbs.forEach((crumb, index) => {
            const listItem = document.createElement('li');
            listItem.className = `breadcrumb-item${crumb.active ? ' active' : ''}`;
            
            if (crumb.active) {
                listItem.textContent = crumb.name;
                listItem.setAttribute('aria-current', 'page');
            } else {
                const link = document.createElement('a');
                link.href = crumb.url;
                link.textContent = crumb.name;
                listItem.appendChild(link);
            }
            
            breadcrumbList.appendChild(listItem);
        });
    }

    addBreadcrumb(name, url, makeActive = true) {
        // Remove active status from current breadcrumbs
        this.breadcrumbs.forEach(crumb => crumb.active = false);
        
        // Add new breadcrumb
        this.breadcrumbs.push({ name, url, active: makeActive });
        
        this.updateBreadcrumbs();
    }

    removeBreadcrumb(index) {
        if (index >= 0 && index < this.breadcrumbs.length) {
            this.breadcrumbs.splice(index, 1);
            this.updateBreadcrumbs();
        }
    }

    setActive(index) {
        this.breadcrumbs.forEach((crumb, i) => {
            crumb.active = i === index;
        });
        this.updateBreadcrumbs();
    }
}

// Initialize dashboard when DOM is loaded
let reviewManagerDashboard;

document.addEventListener('DOMContentLoaded', function() {
    reviewManagerDashboard = new ReviewManagerDashboard();
    
    // Initialize any additional Sprint 5 features
    initializeAdvancedFeatures();
});

function initializeAdvancedFeatures() {
    // Progressive Web App features
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').catch(() => {
            // Service worker registration failed, continue normally
        });
    }
    
    // Performance observer for Core Web Vitals
    if ('PerformanceObserver' in window) {
        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'largest-contentful-paint') {
                    console.log('LCP:', entry.startTime);
                }
            }
        }).observe({ entryTypes: ['largest-contentful-paint'] });
    }
    
    // Add resize observer for responsive adjustments
    if ('ResizeObserver' in window) {
        const resizeObserver = new ResizeObserver(entries => {
            entries.forEach(entry => {
                if (entry.target.classList.contains('sessions-grid')) {
                    // Adjust grid layout based on container size
                    adjustGridLayout(entry.contentRect.width);
                }
            });
        });
        
        const grid = document.querySelector('.sessions-grid');
        if (grid) {
            resizeObserver.observe(grid);
        }
    }
}

function adjustGridLayout(width) {
    const grid = document.querySelector('.sessions-grid');
    if (!grid) return;
    
    // Dynamic grid columns based on container width
    let columns;
    if (width < 600) columns = 1;
    else if (width < 900) columns = 2;
    else if (width < 1200) columns = 3;
    else if (width < 1600) columns = 4;
    else columns = 5;
    
    grid.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ReviewManagerDashboard, ContextualHelpManager, BreadcrumbManager };
}
