// Frontend API helpers for Audit Checklist Executions
// Using SvelteKit fe-api routes as proxy to backend

const API_BASE = '/fe-api/audits';

// Checklist Execution CRUD
export const listExecutions = async (params = {}) => {
	const searchParams = new URLSearchParams(params);
	const url = `${API_BASE}/checklist-executions${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
	const response = await fetch(url);
	if (!response.ok) throw new Error('Failed to fetch executions');
	return response.json();
};

export const getExecution = async (id) => {
	const response = await fetch(`${API_BASE}/checklist-executions/${id}/`);
	if (!response.ok) throw new Error('Failed to fetch execution');
	return response.json();
};

export const createExecution = async (data) => {
	const response = await fetch(`${API_BASE}/checklist-executions/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(data)
	});
	if (!response.ok) throw new Error('Failed to create execution');
	return response.json();
};

export const updateExecution = async (id, data) => {
	const response = await fetch(`${API_BASE}/checklist-executions/${id}/`, {
		method: 'PATCH',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(data)
	});
	if (!response.ok) throw new Error('Failed to update execution');
	return response.json();
};

export const deleteExecution = async (id) => {
	const response = await fetch(`${API_BASE}/checklist-executions/${id}/`, {
		method: 'DELETE'
	});
	if (!response.ok) throw new Error('Failed to delete execution');
	return response.ok;
};

export const startExecution = async (id) => {
	const response = await fetch(`${API_BASE}/checklist-executions/${id}/start_execution/`, {
		method: 'POST'
	});
	if (!response.ok) throw new Error('Failed to start execution');
	return response.json();
};

export const completeExecution = async (id) => {
	const response = await fetch(`${API_BASE}/checklist-executions/${id}/complete_execution/`, {
		method: 'POST'
	});
	if (!response.ok) throw new Error('Failed to complete execution');
	return response.json();
};

export const getExecutionSummary = async (id) => {
	const response = await fetch(`${API_BASE}/checklist-executions/${id}/summary/`);
	if (!response.ok) throw new Error('Failed to fetch summary');
	return response.json();
};

// Item Results
export const listItemResults = async (params = {}) => {
	const searchParams = new URLSearchParams(params);
	const url = `${API_BASE}/checklist-item-results${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
	const response = await fetch(url);
	if (!response.ok) throw new Error('Failed to fetch item results');
	return response.json();
};

export const updateItemResult = async (id, data) => {
	const response = await fetch(`${API_BASE}/checklist-item-results/${id}/`, {
		method: 'PATCH',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(data)
	});
	if (!response.ok) throw new Error('Failed to update result');
	return response.json();
};

export const markItemPass = async (id) => {
	const response = await fetch(`${API_BASE}/checklist-item-results/${id}/mark_pass/`, {
		method: 'POST'
	});
	if (!response.ok) throw new Error('Failed to mark as pass');
	return response.json();
};

export const markItemFail = async (id, comments = '') => {
	const response = await fetch(`${API_BASE}/checklist-item-results/${id}/mark_fail/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ comments })
	});
	if (!response.ok) throw new Error('Failed to mark as fail');
	return response.json();
};
