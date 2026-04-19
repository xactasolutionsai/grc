// Frontend API helpers for the Audit Universe
import { BASE_API_URL } from '$lib/utils/constants';

const API_BASE = `${BASE_API_URL}/audits`;

export const listEntities = async (params = {}) => {
    const searchParams = new URLSearchParams(params);
    const url = `${API_BASE}/entities/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch entities');
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
        method: 'PATCH',
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
