// Frontend API helpers for the Audit Universe
// Using SvelteKit fe-api routes as proxy to backend

const API_BASE = '/fe-api/audits';

export const listEntities = async (params = {}) => {
    const searchParams = new URLSearchParams(params);
    const url = `${API_BASE}/entities${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch entities');
    return response.json();
};

export const getEntity = async (id) => {
    const response = await fetch(`${API_BASE}/entities/${id}/`);
    if (!response.ok) throw new Error('Failed to fetch entity');
    return response.json();
};

export const getRelatedEntities = async (id) => {
    const response = await fetch(`${API_BASE}/entities/${id}/related/`);
    if (!response.ok) throw new Error('Failed to fetch related entities');
    return response.json();
};

export const createEntity = async (data) => {
    const response = await fetch(`${API_BASE}/entities/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create entity');
    return response.json();
};

export const updateEntity = async (id, data) => {
    const response = await fetch(`${API_BASE}/entities/${id}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update entity');
    return response.json();
};

export const deleteEntity = async (id) => {
    const response = await fetch(`${API_BASE}/entities/${id}/`, {
        method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete entity');
    return response.ok;
};

export const uploadOrgStructure = async (id, file) => {
    const url = `${API_BASE}/entities/${id}/upload-org-structure/`;
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });
    if (!response.ok) throw new Error('Failed to upload organizational structure');
    return response.json();
};

export const getHierarchy = async (params = {}) => {
    const searchParams = new URLSearchParams(params);
    const url = `${API_BASE}/entities/hierarchy/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch hierarchy');
    return response.json();
};

export const uploadHierarchyCSV = async (file) => {
    const url = `${API_BASE}/entities/upload-hierarchy-csv/`;
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });
    if (!response.ok) throw new Error('Failed to upload hierarchy CSV');
    return response.json();
};

// Processes / Activities API
export const listProcesses = async (entityId) => {
    const response = await fetch(`${API_BASE}/entities/${entityId}/processes/`);
    if (!response.ok) throw new Error('Failed to fetch processes');
    return response.json();
};

export const createProcess = async (entityId, data) => {
    const response = await fetch(`${API_BASE}/entities/${entityId}/processes/`, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to create process');
    return response.json();
};

export const updateProcess = async (entityId, processId, data) => {
    const response = await fetch(`${API_BASE}/entities/${entityId}/processes/${processId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
        headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to update process');
    return response.json();
};

export const deleteProcess = async (entityId, processId) => {
    const response = await fetch(`${API_BASE}/entities/${entityId}/processes/${processId}/`, {
        method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete process');
    return response.ok;
};

export const uploadProcessesCSV = async (entityId, file) => {
    const url = `${API_BASE}/entities/${entityId}/processes/upload-csv/`;
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });
    if (!response.ok) throw new Error('Failed to upload processes CSV');
    return response.json();
};

export const getProcessesLookup = async () => {
    const response = await fetch(`${API_BASE}/entities/processes/lookup/`);
    if (!response.ok) throw new Error('Failed to fetch processes lookup');
    return response.json();
};
