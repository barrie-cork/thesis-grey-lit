/**
 * Notification Management System
 * Handles toast notifications with auto-dismiss and user preferences
 */

class NotificationManager {
    constructor(options = {}) {
        this.container = null;
        this.queue = [];
        this.activeNotifications = new Map();
        this.maxNotifications = options.maxNotifications || 5;
        this.defaultDuration = options.defaultDuration || 5000;
        this.preferences = {
            auto_dismiss_duration: 5000,
            show_status_changes: true,
            show_error_notifications: true,
            show_success_notifications: true,
            notification_position: 'top-right',
            sound_enabled: false
        };
        
        this.init();
    }
    
    /**
     * Initialize the notification system
     */
    init() {
        this.createContainer();
        this.loadPreferences();
        this.setupEventListeners();
    }
    
    /**
     * Create the notification container
     */
    createContainer() {
        // Remove existing container if present
        const existing = document.getElementById('notification-container');
        if (existing) {
            existing.remove();
        }
        
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.className = `notification-container position-${this.preferences.notification_position}`;
        this.container.setAttribute('aria-live', 'polite');
        this.container.setAttribute('aria-label', 'Notifications');
        
        document.body.appendChild(this.container);
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for keyboard events (ESC to dismiss all)
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.dismissAll();
            }
        });
        
        // Handle clicks outside notifications
        document.addEventListener('click', (event) => {
            if (!this.container.contains(event.target)) {
                // Optionally dismiss on outside click
                // this.dismissAll();
            }
        });
    }
    
    /**
     * Load user notification preferences
     */
    async loadPreferences() {
        try {
            const response = await fetch('/review/api/notification-preferences/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.preferences = { ...this.preferences, ...data.preferences };
                    this.updateContainerPosition();
                }
            }
        } catch (error) {
            console.warn('Failed to load notification preferences:', error);
        }
    }
    
    /**
     * Save user notification preferences
     * @param {Object} newPreferences - New preference values
     */
    async savePreferences(newPreferences) {
        try {
            this.preferences = { ...this.preferences, ...newPreferences };
            
            const response = await fetch('/review/api/notification-preferences/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ preferences: this.preferences })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.preferences = data.preferences;
                    this.updateContainerPosition();
                    this.show('success', 'Preferences Saved', 'Your notification preferences have been updated.');
                }
            }
        } catch (error) {
            console.error('Failed to save notification preferences:', error);
            this.show('error', 'Save Failed', 'Could not save your notification preferences.');
        }
    }
    
    /**
     * Update container position based on preferences
     */
    updateContainerPosition() {
        if (this.container) {
            this.container.className = `notification-container position-${this.preferences.notification_position}`;
        }
    }
    
    /**
     * Show a notification
     * @param {string} type - Notification type (success, error, warning, info)
     * @param {string} title - Notification title
     * @param {string} message - Notification message
     * @param {Object} options - Additional options
     */
    show(type, title, message, options = {}) {
        // Check if this type of notification is enabled
        if (!this.shouldShowNotification(type, options)) {
            return null;
        }
        
        const notification = this.createNotification(type, title, message, options);
        this.addToQueue(notification);
        this.processQueue();
        
        return notification.id;
    }
    
    /**
     * Show a status change notification
     * @param {string} sessionId - Session ID
     * @param {string} oldStatus - Previous status
     * @param {string} newStatus - New status
     * @param {Object} serverData - Additional server data
     */
    showStatusChange(sessionId, oldStatus, newStatus, serverData) {
        if (!this.preferences.show_status_changes) {
            return;
        }
        
        const statusMessages = {
            'executing': { type: 'info', icon: 'play', message: 'Search execution started' },
            'processing': { type: 'info', icon: 'cog', message: 'Processing results' },
            'ready_for_review': { type: 'success', icon: 'check', message: 'Results ready for review' },
            'completed': { type: 'success', icon: 'check-circle', message: 'Review completed' },
            'failed': { type: 'error', icon: 'x-circle', message: 'An error occurred' }
        };
        
        const statusInfo = statusMessages[newStatus] || { type: 'info', icon: 'info', message: 'Status updated' };
        
        this.show(
            statusInfo.type,
            `Session Updated`,
            `${serverData.title || 'Session'}: ${statusInfo.message}`,
            {
                icon: statusInfo.icon,
                sessionId: sessionId,
                duration: this.preferences.auto_dismiss_duration,
                actions: [{
                    text: 'View Session',
                    action: () => window.location.href = `/review/session/${sessionId}/`
                }]
            }
        );
    }
    
    /**
     * Check if a notification should be shown based on preferences
     * @param {string} type - Notification type
     * @param {Object} options - Notification options
     * @returns {boolean} Whether to show the notification
     */
    shouldShowNotification(type, options) {
        if (options.force) return true;
        
        switch (type) {
            case 'success':
                return this.preferences.show_success_notifications;
            case 'error':
                return this.preferences.show_error_notifications;
            case 'warning':
            case 'info':
            default:
                return true; // Always show warnings and info
        }
    }
    
    /**
     * Create a notification object
     * @param {string} type - Notification type
     * @param {string} title - Notification title
     * @param {string} message - Notification message
     * @param {Object} options - Additional options
     * @returns {Object} Notification object
     */
    createNotification(type, title, message, options) {
        const notification = {
            id: Date.now() + Math.random(),
            type: type,
            title: title,
            message: message,
            duration: options.duration || this.preferences.auto_dismiss_duration,
            persistent: options.persistent || false,
            actions: options.actions || [],
            icon: options.icon || this.getDefaultIcon(type),
            sessionId: options.sessionId || null,
            timestamp: new Date(),
            element: null,
            timer: null,
            isPaused: false
        };
        
        return notification;
    }
    
    /**
     * Get default icon for notification type
     * @param {string} type - Notification type
     * @returns {string} Icon class name
     */
    getDefaultIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'x-circle',
            'warning': 'alert-triangle',
            'info': 'info'
        };
        return icons[type] || 'info';
    }
    
    /**
     * Add notification to queue
     * @param {Object} notification - Notification object
     */
    addToQueue(notification) {
        this.queue.push(notification);
    }
    
    /**
     * Process the notification queue
     */
    processQueue() {
        // Remove notifications if we have too many
        while (this.activeNotifications.size >= this.maxNotifications && this.queue.length > 0) {
            this.dismissOldest();
        }
        
        // Show queued notifications
        while (this.queue.length > 0 && this.activeNotifications.size < this.maxNotifications) {
            const notification = this.queue.shift();
            this.displayNotification(notification);
        }
    }
    
    /**
     * Display a notification
     * @param {Object} notification - Notification object
     */
    displayNotification(notification) {
        const element = this.createNotificationElement(notification);
        notification.element = element;
        
        this.container.appendChild(element);
        this.activeNotifications.set(notification.id, notification);
        
        // Trigger entrance animation
        requestAnimationFrame(() => {
            element.classList.add('notification-show');
        });
        
        // Set up auto-dismiss timer
        if (!notification.persistent) {
            this.startDismissTimer(notification);
        }
        
        // Play sound if enabled
        if (this.preferences.sound_enabled) {
            this.playNotificationSound(notification.type);
        }
    }
    
    /**
     * Create the DOM element for a notification
     * @param {Object} notification - Notification object
     * @returns {HTMLElement} Notification element
     */
    createNotificationElement(notification) {
        const element = document.createElement('div');
        element.className = `notification notification-${notification.type}`;
        element.setAttribute('role', 'alert');
        element.setAttribute('aria-live', 'assertive');
        element.dataset.notificationId = notification.id;
        
        // Create notification HTML
        element.innerHTML = `
            <div class="notification-icon">
                <i class="icon icon-${notification.icon}" aria-hidden="true"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${this.escapeHtml(notification.title)}</div>
                <div class="notification-message">${this.escapeHtml(notification.message)}</div>
                <div class="notification-timestamp">${this.formatTimestamp(notification.timestamp)}</div>
            </div>
            <div class="notification-actions"></div>
            <button class="notification-close" aria-label="Close notification" title="Close">
                <i class="icon icon-x" aria-hidden="true"></i>
            </button>
        `;
        
        // Add action buttons
        const actionsContainer = element.querySelector('.notification-actions');
        notification.actions.forEach(action => {
            const button = document.createElement('button');
            button.className = 'notification-action-btn';
            button.textContent = action.text;
            button.onclick = () => {
                if (typeof action.action === 'function') {
                    action.action();
                } else if (typeof action.action === 'string') {
                    window.location.href = action.action;
                }
                this.dismiss(notification.id);
            };
            actionsContainer.appendChild(button);
        });
        
        // Add event listeners
        const closeButton = element.querySelector('.notification-close');
        closeButton.onclick = () => this.dismiss(notification.id);
        
        // Pause/resume timer on hover
        element.onmouseenter = () => this.pauseDismissTimer(notification);
        element.onmouseleave = () => this.resumeDismissTimer(notification);
        
        return element;
    }
    
    /**
     * Start auto-dismiss timer for a notification
     * @param {Object} notification - Notification object
     */
    startDismissTimer(notification) {
        if (notification.timer) {
            clearTimeout(notification.timer);
        }
        
        notification.timer = setTimeout(() => {
            this.dismiss(notification.id);
        }, notification.duration);
    }
    
    /**
     * Pause auto-dismiss timer
     * @param {Object} notification - Notification object
     */
    pauseDismissTimer(notification) {
        if (notification.timer && !notification.isPaused) {
            clearTimeout(notification.timer);
            notification.isPaused = true;
        }
    }
    
    /**
     * Resume auto-dismiss timer
     * @param {Object} notification - Notification object
     */
    resumeDismissTimer(notification) {
        if (notification.isPaused && !notification.persistent) {
            notification.isPaused = false;
            this.startDismissTimer(notification);
        }
    }
    
    /**
     * Dismiss a specific notification
     * @param {string} notificationId - Notification ID
     */
    dismiss(notificationId) {
        const notification = this.activeNotifications.get(notificationId);
        if (!notification) return;
        
        // Clear timer
        if (notification.timer) {
            clearTimeout(notification.timer);
        }
        
        // Add exit animation
        notification.element.classList.add('notification-dismissing');
        
        // Remove after animation
        setTimeout(() => {
            if (notification.element.parentNode) {
                notification.element.parentNode.removeChild(notification.element);
            }
            this.activeNotifications.delete(notificationId);
            
            // Process queue for any waiting notifications
            this.processQueue();
        }, 300);
    }
    
    /**
     * Dismiss the oldest notification
     */
    dismissOldest() {
        const oldestId = Array.from(this.activeNotifications.keys())[0];
        if (oldestId) {
            this.dismiss(oldestId);
        }
    }
    
    /**
     * Dismiss all notifications
     */
    dismissAll() {
        const notificationIds = Array.from(this.activeNotifications.keys());
        notificationIds.forEach(id => this.dismiss(id));
        this.queue = []; // Clear queue as well
    }
    
    /**
     * Play notification sound
     * @param {string} type - Notification type
     */
    playNotificationSound(type) {
        // Create and play audio element
        const audio = new Audio();
        const soundFiles = {
            'success': '/static/review_manager/sounds/success.mp3',
            'error': '/static/review_manager/sounds/error.mp3',
            'warning': '/static/review_manager/sounds/warning.mp3',
            'info': '/static/review_manager/sounds/info.mp3'
        };
        
        audio.src = soundFiles[type] || soundFiles['info'];
        audio.volume = 0.3;
        audio.play().catch(() => {
            // Ignore audio play errors (user interaction required)
        });
    }
    
    /**
     * Format timestamp for display
     * @param {Date} timestamp - Timestamp to format
     * @returns {string} Formatted timestamp
     */
    formatTimestamp(timestamp) {
        const now = new Date();
        const diff = now - timestamp;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            const minutes = Math.floor(diff / 60000);
            return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
        } else {
            return timestamp.toLocaleTimeString();
        }
    }
    
    /**
     * Escape HTML characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Get CSRF token
     * @returns {string} CSRF token
     */
    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name=csrf-token]')?.content ||
               this.getCookieValue('csrftoken') || '';
    }
    
    /**
     * Get cookie value
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
     * Get notification statistics
     * @returns {Object} Statistics
     */
    getStats() {
        return {
            activeCount: this.activeNotifications.size,
            queueCount: this.queue.length,
            maxNotifications: this.maxNotifications,
            preferences: this.preferences
        };
    }
    
    /**
     * Destroy the notification manager
     */
    destroy() {
        this.dismissAll();
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
    }
}

// Global notification manager instance
let globalNotificationManager = null;

/**
 * Get or create the global notification manager
 * @returns {NotificationManager} Notification manager instance
 */
function getNotificationManager() {
    if (!globalNotificationManager) {
        globalNotificationManager = new NotificationManager();
    }
    return globalNotificationManager;
}

/**
 * Show a notification using the global manager
 * @param {string} type - Notification type
 * @param {string} title - Notification title
 * @param {string} message - Notification message
 * @param {Object} options - Additional options
 * @returns {string} Notification ID
 */
function showNotification(type, title, message, options = {}) {
    return getNotificationManager().show(type, title, message, options);
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    getNotificationManager();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NotificationManager, getNotificationManager, showNotification };
}