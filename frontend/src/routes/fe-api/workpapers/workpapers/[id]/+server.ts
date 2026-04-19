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
		const apiUrl = `${BASE_API_URL}/workpapers/workpapers/${params.id}/`;

		const response = await fetch(apiUrl, {
			headers: getHeadersWithCookies(request)
		});

		if (!response.ok) {
			error(response.status, 'Failed to fetch workpaper');
		}

		const data = await response.json();

		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error fetching workpaper:', err);
		error(500, 'Internal server error');
	}
};

export const PUT: RequestHandler = async ({ fetch, params, request }) => {
	try {
		const body = await request.json();
		const apiUrl = `${BASE_API_URL}/workpapers/workpapers/${params.id}/`;

		const response = await fetch(apiUrl, {
			method: 'PUT',
			headers: getHeadersWithCookies(request),
			body: JSON.stringify(body),
		});

		if (!response.ok) {
			error(response.status, 'Failed to update workpaper');
		}

		const data = await response.json();

		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error updating workpaper:', err);
		error(500, 'Internal server error');
	}
};

export const DELETE: RequestHandler = async ({ fetch, params, request }) => {
	try {
		const apiUrl = `${BASE_API_URL}/workpapers/workpapers/${params.id}/`;

		const response = await fetch(apiUrl, {
			method: 'DELETE',
			headers: getHeadersWithCookies(request),
		});

		if (!response.ok) {
			error(response.status, 'Failed to delete workpaper');
		}

		return new Response(null, {
			status: 204
		});
	} catch (err) {
		console.error('Error deleting workpaper:', err);
		error(500, 'Internal server error');
	}
};
