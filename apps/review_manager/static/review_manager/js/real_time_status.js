/**
 * Real-time Status Monitoring System
 * Provides live status updates without page refresh
 */

class StatusMonitor {
    constructor(options = {}) {
        this.pollInterval = options.pollInterval || 5000; // 5 seconds default
        this.maxRetries = options.maxRetries || 3;
        this.retryDelay = options.retryDelay || 1000;
        this.sessions = new Map();
        this.callbacks = new Map();
        this.isPolling = false;
        this.pollTimer = null;
        this.retryCount = 0;
        this.lastPollTime = null;
        this.visibilityChangeHandler = this.handleVisibilityChange.bind(this);
        
        // Bind event handlers
        document.addEventListener('visibilitychange', this.visibilityChangeHandler);
        window.addEventListener('beforeunload', () => this.stopMonitoring());
        
        // Initialize notifications
        this.notificationManager = new NotificationManager();
        
        // Debug mode
        this.debug = options.debug || false;
        
        this.log('Status Monitor initialized');
    }
    
    /**
     * Add a session to monitor
     * @param {string} sessionId - The session ID to monitor
     * @param {HTMLElement} statusElement - The DOM element to update
     * @param {Function} callback - Optional callback for status changes
     */
    addSession(sessionId, statusElement, callback = null) {
        if (!sessionId || !statusElement) {
            console.warn('Invalid session or element provided to StatusMonitor');
            return;
        }
        
        this.sessions.set(sessionId, {
            element: statusElement,
            lastStatus: statusElement.dataset.status || 'unknown',
            lastUpdate: new Date(),
            callback: callback,
            progressElement: statusElement.querySelector('.status-progress'),
            progressBar: statusElement.querySelector('.progress-bar'),
            statusText: statusElement.querySelector('.status-text'),
            statusIcon: statusElement.querySelector('.status-icon')
        });
        
        this.log(`Added session ${sessionId} to monitoring`);
        
        // Start monitoring if this is the first session
        if (this.sessions.size === 1 && !this.isPolling) {
            this.startMonitoring();
        }
    }
    
    /**
     * Remove a session from monitoring
     * @param {string} sessionId - The session ID to remove
     */
    removeSession(sessionId) {
        if (this.sessions.has(sessionId)) {
            this.sessions.delete(sessionId);
            this.log(`Removed session ${sessionId} from monitoring`);
            
            // Stop monitoring if no sessions left
            if (this.sessions.size === 0) {
                this.stopMonitoring();
            }
        }
    }
    
    /**
     * Start real-time monitoring
     */
    startMonitoring() {
        if (this.isPolling) {
            this.log('Monitoring already active');
            return;
        }
        
        this.isPolling = true;
        this.retryCount = 0;
        this.log('Starting status monitoring');
        
        // Initial poll
        this.pollStatuses();
        
        // Set up interval polling
        this.pollTimer = setInterval(() => {
            this.pollStatuses();
        }, this.pollInterval);
    }
    
    /**
     * Stop real-time monitoring
     */
    stopMonitoring() {
        if (!this.isPolling) {
            return;
        }
        
        this.isPolling = false;
        
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
        
        this.log('Stopped status monitoring');
    }
    
    /**
     * Handle browser visibility change
     */
    handleVisibilityChange() {
        if (document.hidden) {
            this.log('Page hidden, stopping monitoring');
            this.stopMonitoring();
        } else {
            this.log('Page visible, resuming monitoring');
            if (this.sessions.size > 0) {
                this.startMonitoring();
            }
        }
    }
    
    /**
     * Poll status updates from the server
     */
    async pollStatuses() {
        if (this.sessions.size === 0) {
            this.log('No sessions to poll');
            return;
        }
        
        const sessionIds = Array.from(this.sessions.keys());
        this.log(`Polling status for ${sessionIds.length} sessions`);
        
        try {
            const response = await fetch('/review/api/status-check/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ session_ids: sessionIds })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.updateStatuses(data.sessions);
                this.retryCount = 0; // Reset retry count on success
                
                // Update poll interval if server suggests optimization
                if (data.poll_interval && data.poll_interval !== this.pollInterval) {
                    this.updatePollInterval(data.poll_interval);
                }
            } else {
                throw new Error(data.error || 'Unknown server error');
            }
            
            this.lastPollTime = new Date();
            
        } catch (error) {
            this.handlePollError(error);
        }
    }
    
    /**
     * Update status displays based on server response
     * @param {Object} sessionsData - Session data from server
     */
    updateStatuses(sessionsData) {
        for (const [sessionId, sessionInfo] of this.sessions) {
            const serverData = sessionsData[sessionId];
            
            if (!serverData) {
                this.log(`No server data for session ${sessionId}`);
                continue;
            }
            
            const currentStatus = sessionInfo.lastStatus;
            const newStatus = serverData.status;
            
            // Check if status changed
            if (currentStatus !== newStatus) {
                this.log(`Status change for session ${sessionId}: ${currentStatus} → ${newStatus}`);
                this.updateSessionStatus(sessionId, sessionInfo, serverData);
                
                // Show notification for status change
                this.notificationManager.showStatusChange(sessionId, currentStatus, newStatus, serverData);
                
                // Call custom callback if provided
                if (sessionInfo.callback) {
                    try {
                        sessionInfo.callback(sessionId, newStatus, currentStatus, serverData);
                    } catch (error) {
                        console.error('Callback error:', error);
                    }
                }
            }
            
            // Update progress information
            this.updateSessionProgress(sessionId, sessionInfo, serverData);
            
            // Update last known status
            sessionInfo.lastStatus = newStatus;
            sessionInfo.lastUpdate = new Date();
        }
    }
    
    /**
     * Update session status display
     * @param {string} sessionId - Session ID
     * @param {Object} sessionInfo - Session monitoring info
     * @param {Object} serverData - Server response data
     */
    updateSessionStatus(sessionId, sessionInfo, serverData) {
        const element = sessionInfo.element;
        const newStatus = serverData.status;
        const displayText = serverData.status_display;
        
        // Add updating animation
        element.classList.add('updating');
        
        setTimeout(() => {
            // Update status class
            element.className = element.className.replace(/status-\w+/g, '');
            element.classList.add(`status-${newStatus}`);
            element.dataset.status = newStatus;
            
            // Update status text
            if (sessionInfo.statusText) {
                sessionInfo.statusText.textContent = displayText;
            }
            
            // Update status icon
            if (sessionInfo.statusIcon) {
                sessionInfo.statusIcon.className = sessionInfo.statusIcon.className.replace(/icon-\w+/g, '');
                sessionInfo.statusIcon.classList.add(`icon-${newStatus}`);
            }
            
            // Remove updating animation
            element.classList.remove('updating');
            
            // Add status change animation
            element.classList.add('status-changed');
            setTimeout(() => {
                element.classList.remove('status-changed');
            }, 1000);
            
        }, 200); // Small delay for smooth transition
    }
    
    /**
     * Update session progress display
     * @param {string} sessionId - Session ID
     * @param {Object} sessionInfo - Session monitoring info
     * @param {Object} serverData - Server response data
     */
    updateSessionProgress(sessionId, sessionInfo, serverData) {
        const progress = serverData.progress;
        const progressElement = sessionInfo.progressElement;
        const progressBar = sessionInfo.progressBar;
        
        if (progress !== null && progress !== undefined && progressElement && progressBar) {
            // Show progress bar
            progressElement.style.display = 'block';
            
            // Update progress width
            progressBar.style.width = `${progress}%`;
            
            // Add progress message if available
            if (serverData.progress_message) {
                progressElement.title = serverData.progress_message;
            }
            
            // Hide progress bar when complete
            if (progress >= 100) {
                setTimeout(() => {
                    progressElement.style.display = 'none';
                }, 2000);
            }
        } else if (progressElement) {
            // Hide progress bar if no progress data
            progressElement.style.display = 'none';
        }
    }
    
    /**
     * Handle polling errors with retry logic
     * @param {Error} error - The error that occurred
     */
    handlePollError(error) {
        this.log(`Poll error: ${error.message}`);
        this.retryCount++;
        
        if (this.retryCount <= this.maxRetries) {
            this.log(`Retrying in ${this.retryDelay}ms (attempt ${this.retryCount}/${this.maxRetries})`);
            
            setTimeout(() => {
                this.pollStatuses();
            }, this.retryDelay);
            
            // Exponential backoff
            this.retryDelay *= 2;
        } else {
            this.log('Max retries reached, stopping monitoring');
            this.stopMonitoring();
            
            // Show error notification
            this.notificationManager.show('error', 'Connection Lost', 
                'Unable to get real-time updates. Please refresh the page.', {
                persistent: true,
                actions: [{
                    text: 'Refresh',
                    action: () => window.location.reload()
                }]
            });
        }
    }
    
    /**
     * Update polling interval
     * @param {number} newInterval - New interval in milliseconds
     */
    updatePollInterval(newInterval) {
        if (newInterval !== this.pollInterval) {
            this.log(`Updating poll interval: ${this.pollInterval}ms → ${newInterval}ms`);
            this.pollInterval = newInterval;
            
            // Restart polling with new interval
            if (this.isPolling) {
                this.stopMonitoring();
                this.startMonitoring();
            }
        }
    }
    
    /**
     * Get CSRF token for requests
     * @returns {string} CSRF token
     */
    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     document.querySelector('meta[name=csrf-token]')?.content ||
                     this.getCookieValue('csrftoken');
        
        if (!token) {
            console.warn('CSRF token not found');
        }
        
        return token || '';
    }
    
    /**
     * Get cookie value by name
     * @param {string} name - Cookie name
     * @returns {string} Cookie value
     */
    getCookieValue(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return '';
    }
    
    /**
     * Log debug messages
     * @param {string} message - Message to log
     */
    log(message) {
        if (this.debug) {
            console.log(`[StatusMonitor] ${message}`);
        }
    }
    
    /**
     * Get monitoring statistics
     * @returns {Object} Statistics object
     */
    getStats() {
        return {
            isPolling: this.isPolling,
            sessionCount: this.sessions.size,
            pollInterval: this.pollInterval,
            retryCount: this.retryCount,
            lastPollTime: this.lastPollTime,
            sessions: Array.from(this.sessions.keys())
        };
    }
    
    /**
     * Cleanup and destroy the monitor
     */
    destroy() {
        this.stopMonitoring();
        document.removeEventListener('visibilitychange', this.visibilityChangeHandler);
        this.sessions.clear();
        this.callbacks.clear();
        this.log('Status Monitor destroyed');
    }
}

// Global status monitor instance
let globalStatusMonitor = null;

/**
 * Initialize status monitoring for the page
 * @param {Object} options - Configuration options
 * @returns {StatusMonitor} Status monitor instance
 */
function initializeStatusMonitoring(options = {}) {
    if (globalStatusMonitor) {
        globalStatusMonitor.destroy();
    }
    
    globalStatusMonitor = new StatusMonitor(options);
    
    // Auto-discover status elements on the page
    const statusElements = document.querySelectorAll('[data-session-id]');
    statusElements.forEach(element => {
        const sessionId = element.dataset.sessionId;
        if (sessionId) {
            globalStatusMonitor.addSession(sessionId, element);
        }
    });
    
    return globalStatusMonitor;
}

/**
 * Get the global status monitor instance
 * @returns {StatusMonitor|null} Status monitor instance
 */
function getStatusMonitor() {
    return globalStatusMonitor;
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeStatusMonitoring({
        debug: window.DEBUG_MODE || false
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { StatusMonitor, initializeStatusMonitoring, getStatusMonitor };
}