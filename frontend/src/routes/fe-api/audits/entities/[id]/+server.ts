import { BASE_API_URL } from '$lib/utils/constants';
import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ fetch, params }) => {
	try {
		const apiUrl = `${BASE_API_URL}/audits/entities/${params.id}/`;
		
		const response = await fetch(apiUrl, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
			},
		});
		
		if (!response.ok) {
			error(response.status, 'Failed to fetch entity');
		}
		
		const data = await response.json();
		
		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error fetching audit entity:', err);
		error(500, 'Internal server error');
	}
};

export const PATCH: RequestHandler = async ({ fetch, request, params }) => {
	try {
		const body = await request.json();
		const apiUrl = `${BASE_API_URL}/audits/entities/${params.id}/`;
		
		const response = await fetch(apiUrl, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(body),
		});
		
		if (!response.ok) {
			error(response.status, 'Failed to update entity');
		}
		
		const data = await response.json();
		
		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error updating audit entity:', err);
		error(500, 'Internal server error');
	}
};

export const PUT: RequestHandler = async ({ fetch, request, params }) => {
	try {
		const body = await request.json();
		const apiUrl = `${BASE_API_URL}/audits/entities/${params.id}/`;
		
		const response = await fetch(apiUrl, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(body),
		});
		
		if (!response.ok) {
			error(response.status, 'Failed to update entity');
		}
		
		const data = await response.json();
		
		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error updating audit entity:', err);
		error(500, 'Internal server error');
	}
};

export const DELETE: RequestHandler = async ({ fetch, params }) => {
	try {
		const apiUrl = `${BASE_API_URL}/audits/entities/${params.id}/`;
		
		const response = await fetch(apiUrl, {
			method: 'DELETE',
		});
		
		if (!response.ok) {
			error(response.status, 'Failed to delete entity');
		}
		
		return new Response(JSON.stringify({ success: true }), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error deleting audit entity:', err);
		error(500, 'Internal server error');
	}
};
