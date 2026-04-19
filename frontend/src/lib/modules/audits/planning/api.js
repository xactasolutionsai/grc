// Frontend API helpers for Audit Planning
// Using SvelteKit fe-api routes as proxy to backend

const API_BASE = '/fe-api/audits';

// List audit plans with optional filtering
export async function listPlans(params = {}) {
	const searchParams = new URLSearchParams();

	// Add query parameters
	Object.entries(params).forEach(([key, value]) => {
		if (value !== null && value !== undefined && value !== '') {
			searchParams.append(key, value);
		}
	});

	const url = `${API_BASE}/plans${searchParams.toString() ? '?' + searchParams.toString() : ''}`;

	const response = await fetch(url, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include'
	});

	if (!response.ok) {
		throw new Error(`Failed to load audit plans: ${response.status}`);
	}

	return await response.json();
}

// Get a single audit plan
export async function getPlan(id) {
	const response = await fetch(`${API_BASE}/plans/${id}/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include'
	});

	if (!response.ok) {
		throw new Error(`Failed to load audit plan: ${response.status}`);
	}

	return await response.json();
}

// Create a new audit plan
export async function createPlan(data) {
	const response = await fetch(`${API_BASE}/plans/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include',
		body: JSON.stringify(data)
	});

	if (!response.ok) {
		const errorData = await response.json();
		throw new Error(errorData.detail || `Failed to create audit plan: ${response.status}`);
	}

	return await response.json();
}

// Update an existing audit plan
export async function updatePlan(id, data) {
	const response = await fetch(`${API_BASE}/plans/${id}/`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include',
		body: JSON.stringify(data)
	});

	if (!response.ok) {
		const errorData = await response.json();
		throw new Error(errorData.detail || `Failed to update audit plan: ${response.status}`);
	}

	return await response.json();
}

// Delete an audit plan
export async function deletePlan(id) {
	const response = await fetch(`${API_BASE}/plans/${id}/`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include'
	});

	if (!response.ok) {
		throw new Error(`Failed to delete audit plan: ${response.status}`);
	}
}
