import { BASE_API_URL } from '$lib/utils/constants';
import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Helper function to forward cookies
function getHeadersWithCookies(request: Request): Record<string, string> {
	const cookieHeader = request.headers.get('cookie');
	const headers: Record<string, string> = {
		'Content-Type': 'application/json'
	};
	if (cookieHeader) {
		headers['Cookie'] = cookieHeader;
	}
	return headers;
}

export const GET: RequestHandler = async ({ fetch, params, request }) => {
	try {
		const { id } = params;
		const apiUrl = `${BASE_API_URL}/audits/plans/${id}/`;

		const response = await fetch(apiUrl, {
			headers: getHeadersWithCookies(request)
		});

		if (!response.ok) {
			error(response.status, 'Failed to fetch plan');
		}

		const data = await response.json();

		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error fetching audit plan:', err);
		error(500, 'Internal server error');
	}
};

export const PUT: RequestHandler = async ({ fetch, params, request }) => {
	try {
		const { id } = params;
		const body = await request.json();
		const apiUrl = `${BASE_API_URL}/audits/plans/${id}/`;

		const response = await fetch(apiUrl, {
			method: 'PUT',
			headers: getHeadersWithCookies(request),
			body: JSON.stringify(body),
		});

		if (!response.ok) {
			error(response.status, 'Failed to update plan');
		}

		const data = await response.json();

		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error updating audit plan:', err);
		error(500, 'Internal server error');
	}
};

export const DELETE: RequestHandler = async ({ fetch, params, request }) => {
	try {
		const { id } = params;
		const apiUrl = `${BASE_API_URL}/audits/plans/${id}/`;

		const response = await fetch(apiUrl, {
			method: 'DELETE',
			headers: getHeadersWithCookies(request)
		});

		if (!response.ok) {
			error(response.status, 'Failed to delete plan');
		}

		return new Response(JSON.stringify({ success: true }), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error deleting audit plan:', err);
		error(500, 'Internal server error');
	}
};
