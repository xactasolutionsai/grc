// Frontend API helpers for Workpapers & Evidence module
// Using SvelteKit fe-api routes as proxy to backend

const API_BASE = '/fe-api/workpapers';

/**
 * List workpapers with optional filtering
 * @param {Object} params - Query parameters (status, workpaper_type, my_uploads, etc.)
 * @returns {Promise<Object>} List of workpapers
 */
export const listWorkpapers = async (params = {}) => {
    const searchParams = new URLSearchParams(params);
    const url = `${API_BASE}/workpapers${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch workpapers');
    return response.json();
};

/**
 * Get a single workpaper by ID
 * @param {string|number} id - Workpaper ID
 * @returns {Promise<Object>} Workpaper details
 */
export const getWorkpaper = async (id) => {
    const response = await fetch(`${API_BASE}/workpapers/${id}/`);
    if (!response.ok) throw new Error('Failed to fetch workpaper');
    return response.json();
};

/**
 * Create a new workpaper
 * @param {Object} data - Workpaper data
 * @returns {Promise<Object>} Created workpaper
 */
export const createWorkpaper = async (data) => {
    const response = await fetch(`${API_BASE}/workpapers/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create workpaper');
    return response.json();
};

/**
 * Update an existing workpaper
 * @param {string|number} id - Workpaper ID
 * @param {Object} data - Updated workpaper data
 * @returns {Promise<Object>} Updated workpaper
 */
export const updateWorkpaper = async (id, data) => {
    const response = await fetch(`${API_BASE}/workpapers/${id}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update workpaper');
    return response.json();
};

/**
 * Delete a workpaper
 * @param {string|number} id - Workpaper ID
 * @returns {Promise<boolean>} Success status
 */
export const deleteWorkpaper = async (id) => {
    const response = await fetch(`${API_BASE}/workpapers/${id}/`, {
        method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete workpaper');
    return response.ok;
};

/**
 * Upload a file to a workpaper
 * @param {string|number} id - Workpaper ID
 * @param {File} file - File to upload
 * @returns {Promise<Object>} Updated workpaper
 */
export const uploadFile = async (id, file) => {
    const url = `${API_BASE}/workpapers/${id}/upload_file/`;
    const formData = new FormData();
    formData.append('file', file);

    // Create abort controller for timeout (2 minutes for larger files)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout

    try {
        console.log('[API] Uploading to:', url);
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            signal: controller.signal
        });

        clearTimeout(timeoutId);
        console.log('[API] Upload response received:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('[API] Upload failed:', errorText);
            throw new Error(`Failed to upload file: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        console.log('[API] Upload successful');
        return result;
    } catch (error) {
        clearTimeout(timeoutId);
        console.error('[API] Upload error:', error);
        if (error.name === 'AbortError') {
            throw new Error('File upload timeout - the server is taking too long to respond. Please try again or contact support if the issue persists.');
        }
        throw error;
    }
};

/**
 * Delete the file attached to a workpaper
 * @param {string|number} id - Workpaper ID
 * @returns {Promise<Object>} Response message
 */
export const deleteFile = async (id) => {
    const response = await fetch(`${API_BASE}/workpapers/${id}/delete_file/`, {
        method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete file');
    return response.json();
};

/**
 * Submit workpaper for review
 * @param {string|number} id - Workpaper ID
 * @returns {Promise<Object>} Updated workpaper
 */
export const submitForReview = async (id) => {
    const response = await fetch(`${API_BASE}/workpapers/${id}/submit_for_review/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    });
    if (!response.ok) throw new Error('Failed to submit for review');
    return response.json();
};

/**
 * Mark workpaper as reviewed
 * @param {string|number} id - Workpaper ID
 * @param {string} comments - Optional comments
 * @returns {Promise<Object>} Updated workpaper
 */
export const reviewWorkpaper = async (id, comments = '') => {
    const response = await fetch(`${API_BASE}/workpapers/${id}/review/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comments }),
    });
    if (!response.ok) throw new Error('Failed to review workpaper');
    return response.json();
};

/**
 * Approve a workpaper
 * @param {string|number} id - Workpaper ID
 * @param {string} comments - Optional comments
 * @returns {Promise<Object>} Updated workpaper
 */
export const approveWorkpaper = async (id, comments = '') => {
    const response = await fetch(`${API_BASE}/workpapers/${id}/approve/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'approve', comments }),
    });
    if (!response.ok) throw new Error('Failed to approve workpaper');
    return response.json();
};

/**
 * Reject a workpaper
 * @param {string|number} id - Workpaper ID
 * @param {string} reason - Rejection reason (required)
 * @returns {Promise<Object>} Updated workpaper
 */
export const rejectWorkpaper = async (id, reason) => {
    const response = await fetch(`${API_BASE}/workpapers/${id}/reject/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'reject', reason }),
    });
    if (!response.ok) throw new Error('Failed to reject workpaper');
    return response.json();
};

/**
 * Get approval history for a workpaper
 * @param {string|number} id - Workpaper ID
 * @returns {Promise<Array>} Approval history
 */
export const getApprovalHistory = async (id) => {
    const response = await fetch(`${API_BASE}/workpapers/${id}/approval_history/`);
    if (!response.ok) throw new Error('Failed to fetch approval history');
    return response.json();
};

/**
 * List all approval records with optional filtering
 * @param {Object} params - Query parameters (workpaper, action, action_by)
 * @returns {Promise<Object>} List of approval records
 */
export const listApprovals = async (params = {}) => {
    const searchParams = new URLSearchParams(params);
    const url = `${API_BASE}/approvals${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch approvals');
    return response.json();
};
