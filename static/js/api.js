/**
 * EcoProtect API Client
 * Manages all asynchronous communication with the Python / SQLite backend.
 */

const API = {
    // Generic Fetch Wrapper
    async request(endpoint, options = {}) {
        try {
            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    ...(options.headers || {})
                },
                ...options
            };
            const response = await fetch(endpoint, config);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error(`API Error on ${endpoint}:`, error);
            return { status: 'error', message: 'Network or server communication error.' };
        }
    },

    // Environmental Statistics
    async getStats() {
        return await this.request('/api/stats');
    },

    // Articles & News
    async getArticles(category = 'all', search = '') {
        let url = `/api/articles?category=${encodeURIComponent(category)}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        return await this.request(url);
    },

    async getArticle(id) {
        return await this.request(`/api/articles/${id}`);
    },

    async createArticle(payload) {
        return await this.request('/api/articles', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async deleteArticle(id) {
        return await this.request(`/api/articles/${id}`, { method: 'DELETE' });
    },

    // Environmental Events
    async getEvents(category = 'all') {
        return await this.request(`/api/events?category=${encodeURIComponent(category)}`);
    },

    async registerEvent(eventId, payload) {
        return await this.request(`/api/events/${eventId}/register`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async createEvent(payload) {
        return await this.request('/api/events', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async deleteEvent(id) {
        return await this.request(`/api/events/${id}`, { method: 'DELETE' });
    },

    // Feedback & Contact
    async submitFeedback(payload) {
        return await this.request('/api/feedback', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async getFeedback() {
        return await this.request('/api/feedback');
    },

    async updateFeedbackStatus(id, status) {
        return await this.request(`/api/feedback/${id}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status })
        });
    },

    // "One Planet, One Responsibility" Campaign Pledges
    async submitPledge(payload) {
        return await this.request('/api/pledges', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async getPledges() {
        return await this.request('/api/pledges');
    },

    // Newsletter
    async subscribeNewsletter(email) {
        return await this.request('/api/newsletter', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    },

    // Scientific Calculator (Bridge to C++ Engine & Python Fallback)
    async calculateImpact(payload) {
        return await this.request('/api/calculate', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    // User Authentication & Session
    async register(payload) {
        return await this.request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async login(identifier, password, rememberMe = true) {
        return await this.request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ identifier, password, remember_me: rememberMe })
        });
    },

    async getCurrentUser() {
        return await this.request('/api/auth/me');
    },

    async logout() {
        return await this.request('/api/auth/logout', { method: 'POST' });
    },

    // Dashboard & Environmental Control
    async getDashboardStats() {
        return await this.request('/api/dashboard/stats');
    },

    async logEcoAction(payload) {
        return await this.request('/api/dashboard/log-action', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async simulateMitigation(payload) {
        return await this.request('/api/dashboard/simulate', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    // Admin Auth & Stats
    async adminLogin(username, password) {
        return await this.request('/api/admin/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    },

    async getAdminOverview() {
        return await this.request('/api/admin/overview');
    }
};

// UI Notification Toast
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';

    toast.innerHTML = `
        <span style="font-size: 1.2rem;">${icon}</span>
        <div style="font-size: 0.9rem; font-weight: 500;">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
