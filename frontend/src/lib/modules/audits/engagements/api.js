// Frontend API helpers for Audit Engagements
const API_BASE = '/fe-api/audits';

// Helper function to get auth headers
const getAuthHeaders = () => {
    return {
        'Content-Type': 'application/json'
    };
};

// Helper function to handle API responses
const handleResponse = async (response) => {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // Handle validation errors (DRF returns field-specific errors)
        if (errorData && typeof errorData === 'object' && !errorData.detail) {
            const errors = Object.entries(errorData)
                .map(([field, messages]) => {
                    const msg = Array.isArray(messages) ? messages.join(', ') : messages;
                    return `${field}: ${msg}`;
                })
                .join('; ');
            throw new Error(errors || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        throw new Error(errorData.detail || errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
};

// CRUD Operations
export const listEngagements = async (params = {}) => {
    const searchParams = new URLSearchParams(params);
    const url = `${API_BASE}/engagements${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url, {
        headers: getAuthHeaders(),
        credentials: 'include'
    });
    return handleResponse(response);
};

export const getEngagement = async (id) => {
    const response = await fetch(`${API_BASE}/engagements/${id}/`, {
        headers: getAuthHeaders(),
        credentials: 'include'
    });
    return handleResponse(response);
};

export const createEngagement = async (data) => {
    const response = await fetch(`${API_BASE}/engagements/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify(data),
    });
    return handleResponse(response);
};

export const updateEngagement = async (id, data) => {
    const response = await fetch(`${API_BASE}/engagements/${id}/`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify(data),
    });
    return handleResponse(response);
};

export const deleteEngagement = async (id) => {
    const response = await fetch(`${API_BASE}/engagements/${id}/`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
        credentials: 'include'
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    return response.ok;
};

// Engagement Actions
export const startEngagement = async (id) => {
    const response = await fetch(`${API_BASE}/engagements/${id}/start/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include'
    });
    return handleResponse(response);
};

export const submitResults = async (id, data = {}) => {
    const response = await fetch(`${API_BASE}/engagements/${id}/submit-results/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify(data),
    });
    return handleResponse(response);
};

export const closeEngagement = async (id, data = {}) => {
    const response = await fetch(`${API_BASE}/engagements/${id}/close/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify(data),
    });
    return handleResponse(response);
};

export const updateProgress = async (id, data) => {
    const response = await fetch(`${API_BASE}/engagements/${id}/update-progress/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify(data),
    });
    return handleResponse(response);
};

// Additional endpoints
export const getEngagementTimeline = async (id) => {
    const response = await fetch(`${API_BASE}/engagements/${id}/timeline/`, {
        headers: getAuthHeaders(),
        credentials: 'include'
    });
    return handleResponse(response);
};

export const getEngagementCalendar = async (params = {}) => {
    const searchParams = new URLSearchParams(params);
    const url = `${API_BASE}/engagements/calendar/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url, {
        headers: getAuthHeaders(),
        credentials: 'include'
    });
    return handleResponse(response);
};

export const getEngagementStatistics = async (params = {}) => {
    const searchParams = new URLSearchParams(params);
    const url = `${API_BASE}/engagements/statistics/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url, {
        headers: getAuthHeaders(),
        credentials: 'include'
    });
    return handleResponse(response);
};

export const getEngagementSummary = async (params = {}) => {
    const searchParams = new URLSearchParams(params);
    const url = `${API_BASE}/engagements/summary/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url, {
        headers: getAuthHeaders(),
        credentials: 'include'
    });
    return handleResponse(response);
};

export const getMyEngagements = async (params = {}) => {
    return listEngagements({ ...params, my_engagements: 'true' });
};

export const getMyTeamEngagements = async (params = {}) => {
    return listEngagements({ ...params, my_team: 'true' });
};

// Filter and search helpers
export const getEngagementsByStatus = async (status) => {
    return listEngagements({ status });
};

export const getEngagementsByPriority = async (priority) => {
    return listEngagements({ priority });
};

export const getEngagementsByAuditType = async (auditType) => {
    return listEngagements({ audit_type: auditType });
};

export const getEngagementsByAuditPlan = async (auditPlanId) => {
    return listEngagements({ audit_plan: auditPlanId });
};

export const getEngagementsByEntity = async (entityId) => {
    return listEngagements({ entity: entityId });
};

export const getEngagementsByAuditor = async (auditorId) => {
    return listEngagements({ assigned_auditor: auditorId });
};

export const getEngagementsByLead = async (leadId) => {
    return listEngagements({ engagement_lead: leadId });
};

export const getOverdueEngagements = async () => {
    return listEngagements({ overdue: 'true' });
};

export const searchEngagements = async (query) => {
    return listEngagements({ search: query });
};

// Date range filters
export const getEngagementsByDateRange = async (startDate, endDate) => {
    const params = {};
    if (startDate) params.planned_start_date__gte = startDate;
    if (endDate) params.planned_end_date__lte = endDate;
    return listEngagements(params);
};

// Calendar helpers
export const getEngagementsForMonth = async (year, month) => {
    return getEngagementCalendar({ year, month });
};

// Status and priority constants
export const ENGAGEMENT_STATUSES = [
    { value: 'draft', label: 'Draft' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'fieldwork', label: 'Fieldwork' },
    { value: 'review', label: 'Review' },
    { value: 'submitted', label: 'Submitted' },
    { value: 'closed', label: 'Closed' },
    { value: 'cancelled', label: 'Cancelled' }
];

export const ENGAGEMENT_PRIORITIES = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' }
];

export const AUDIT_TYPES = [
    { value: 'internal', label: 'Internal Audit' },
    { value: 'external', label: 'External Audit' },
    { value: 'it_audit', label: 'IT Audit' },
    { value: 'compliance', label: 'Compliance Audit' },
    { value: 'financial', label: 'Financial Audit' },
    { value: 'operational', label: 'Operational Audit' },
    { value: 'risk_assessment', label: 'Risk Assessment' }
];

// Status color mapping
export const STATUS_COLORS = {
    draft: 'gray',
    in_progress: 'blue',
    fieldwork: 'yellow',
    review: 'orange',
    submitted: 'green',
    closed: 'gray',
    cancelled: 'red'
};

// Priority color mapping
export const PRIORITY_COLORS = {
    low: 'green',
    medium: 'yellow',
    high: 'orange',
    critical: 'red'
};

// Helper functions
export const canStartEngagement = (engagement) => {
    return engagement?.can_be_started === true;
};

export const canSubmitResults = (engagement) => {
    return engagement?.can_submit_results === true;
};

export const canCloseEngagement = (engagement) => {
    return engagement?.can_be_closed === true;
};

export const isEngagementOverdue = (engagement) => {
    return engagement?.is_overdue === true;
};

export const getEngagementDuration = (engagement) => {
    return engagement?.duration_days || 0;
};

export const getActualDuration = (engagement) => {
    return engagement?.actual_duration_days || 0;
};

export const formatEngagementStatus = (status) => {
    const statusObj = ENGAGEMENT_STATUSES.find(s => s.value === status);
    return statusObj ? statusObj.label : status;
};

export const formatEngagementPriority = (priority) => {
    const priorityObj = ENGAGEMENT_PRIORITIES.find(p => p.value === priority);
    return priorityObj ? priorityObj.label : priority;
};

