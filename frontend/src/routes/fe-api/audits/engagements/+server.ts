import { BASE_API_URL } from '$lib/utils/constants';
import { json } from '@sveltejs/kit';
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

export const GET: RequestHandler = async ({ url, fetch, request }) => {
	try {
		const searchParams = url.searchParams.toString();
		const apiUrl = `${BASE_API_URL}/audits/engagements/${searchParams ? '?' + searchParams : ''}`;

		const response = await fetch(apiUrl, {
			method: 'GET',
			headers: getHeadersWithCookies(request)
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			// Return the full error data from Django
			return json(errorData.detail ? { error: errorData.detail } : errorData, { status: response.status });
		}

		const data = await response.json();
		return json(data);
	} catch (error) {
		console.error('Error fetching engagements:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};

export const POST: RequestHandler = async ({ request, fetch }) => {
	try {
		const body = await request.json();
		const apiUrl = `${BASE_API_URL}/audits/engagements/`;

		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: getHeadersWithCookies(request),
			body: JSON.stringify(body)
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			// Return the full error data from Django (includes field-specific validation errors)
			return json(errorData, { status: response.status });
		}

		const data = await response.json();
		return json(data);
	} catch (error) {
		console.error('Error creating engagement:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
