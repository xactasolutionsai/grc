import { BASE_API_URL } from '$lib/utils/constants';
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

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

export const GET: RequestHandler = async ({ params, fetch, request }) => {
	try {
		const apiUrl = `${BASE_API_URL}/audits/checklist-items/${params.id}/`;

		const response = await fetch(apiUrl, {
			method: 'GET',
			headers: getHeadersWithCookies(request)
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			return json(errorData, { status: response.status });
		}

		const data = await response.json();
		return json(data);
	} catch (err) {
		console.error('Error fetching checklist item:', err);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};

export const PUT: RequestHandler = async ({ params, request, fetch }) => {
	try {
		const body = await request.json();
		const apiUrl = `${BASE_API_URL}/audits/checklist-items/${params.id}/`;

		const response = await fetch(apiUrl, {
			method: 'PUT',
			headers: getHeadersWithCookies(request),
			body: JSON.stringify(body)
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			return json(errorData, { status: response.status });
		}

		const data = await response.json();
		return json(data);
	} catch (err) {
		console.error('Error updating checklist item:', err);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};

export const PATCH: RequestHandler = async ({ params, request, fetch }) => {
	try {
		const body = await request.json();
		const apiUrl = `${BASE_API_URL}/audits/checklist-items/${params.id}/`;

		const response = await fetch(apiUrl, {
			method: 'PATCH',
			headers: getHeadersWithCookies(request),
			body: JSON.stringify(body)
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			return json(errorData, { status: response.status });
		}

		const data = await response.json();
		return json(data);
	} catch (err) {
		console.error('Error updating checklist item:', err);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};

export const DELETE: RequestHandler = async ({ params, fetch, request }) => {
	try {
		const apiUrl = `${BASE_API_URL}/audits/checklist-items/${params.id}/`;

		const response = await fetch(apiUrl, {
			method: 'DELETE',
			headers: getHeadersWithCookies(request)
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			return json(errorData, { status: response.status });
		}

		return new Response(null, { status: 204 });
	} catch (err) {
		console.error('Error deleting checklist item:', err);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
