// Frontend API helpers for Audit Checklists
// Using SvelteKit fe-api routes as proxy to backend

const API_BASE = '/fe-api/audits';

// Checklist CRUD operations
export const listChecklists = async (params = {}) => {
	const searchParams = new URLSearchParams(params);
	const url = `${API_BASE}/checklists${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
	const response = await fetch(url);
	if (!response.ok) throw new Error('Failed to fetch checklists');
	return response.json();
};

export const getChecklist = async (id) => {
	const response = await fetch(`${API_BASE}/checklists/${id}/`);
	if (!response.ok) throw new Error('Failed to fetch checklist');
	return response.json();
};

export const createChecklist = async (data) => {
	const response = await fetch(`${API_BASE}/checklists/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		const errorMessage = errorData.folder
			? `Folder: ${Array.isArray(errorData.folder) ? errorData.folder.join(', ') : errorData.folder}`
			: errorData.detail || 'Failed to create checklist';
		throw new Error(errorMessage);
	}
	return response.json();
};

export const updateChecklist = async (id, data) => {
	const response = await fetch(`${API_BASE}/checklists/${id}/`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		const errorMessage = errorData.folder
			? `Folder: ${Array.isArray(errorData.folder) ? errorData.folder.join(', ') : errorData.folder}`
			: errorData.detail || 'Failed to update checklist';
		throw new Error(errorMessage);
	}
	return response.json();
};

export const patchChecklist = async (id, data) => {
	const response = await fetch(`${API_BASE}/checklists/${id}/`, {
		method: 'PATCH',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (!response.ok) throw new Error('Failed to update checklist');
	return response.json();
};

export const deleteChecklist = async (id) => {
	const response = await fetch(`${API_BASE}/checklists/${id}/`, {
		method: 'DELETE'
	});
	if (!response.ok) throw new Error('Failed to delete checklist');
	return response.ok;
};

export const duplicateChecklist = async (id) => {
	const response = await fetch(`${API_BASE}/checklists/${id}/duplicate/`, {
		method: 'POST'
	});
	if (!response.ok) throw new Error('Failed to duplicate checklist');
	return response.json();
};

// ChecklistItem CRUD operations
export const listChecklistItems = async (params = {}) => {
	const searchParams = new URLSearchParams(params);
	const url = `${API_BASE}/checklist-items${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
	const response = await fetch(url);
	if (!response.ok) throw new Error('Failed to fetch checklist items');
	return response.json();
};

export const getChecklistItem = async (id) => {
	const response = await fetch(`${API_BASE}/checklist-items/${id}/`);
	if (!response.ok) throw new Error('Failed to fetch checklist item');
	return response.json();
};

export const createChecklistItem = async (data) => {
	const response = await fetch(`${API_BASE}/checklist-items/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (!response.ok) throw new Error('Failed to create checklist item');
	return response.json();
};

export const updateChecklistItem = async (id, data) => {
	const response = await fetch(`${API_BASE}/checklist-items/${id}/`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (!response.ok) throw new Error('Failed to update checklist item');
	return response.json();
};

export const patchChecklistItem = async (id, data) => {
	const response = await fetch(`${API_BASE}/checklist-items/${id}/`, {
		method: 'PATCH',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (!response.ok) throw new Error('Failed to update checklist item');
	return response.json();
};

export const deleteChecklistItem = async (id) => {
	const response = await fetch(`${API_BASE}/checklist-items/${id}/`, {
		method: 'DELETE'
	});
	if (!response.ok) throw new Error('Failed to delete checklist item');
	return response.ok;
};

export const reorderChecklistItem = async (id, order) => {
	const response = await fetch(`${API_BASE}/checklist-items/${id}/reorder/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ order })
	});
	if (!response.ok) throw new Error('Failed to reorder checklist item');
	return response.json();
};
