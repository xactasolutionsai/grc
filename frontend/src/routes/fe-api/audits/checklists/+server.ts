import { BASE_API_URL } from '$lib/utils/constants';
import { json, error } from '@sveltejs/kit';
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

export const GET: RequestHandler = async ({ url, fetch, request }) => {
	try {
		const searchParams = url.searchParams.toString();
		const apiUrl = `${BASE_API_URL}/audits/checklists/${searchParams ? '?' + searchParams : ''}`;

		const response = await fetch(apiUrl, {
			method: 'GET',
			headers: getHeadersWithCookies(request)
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			return json(errorData.detail ? { error: errorData.detail } : errorData, { status: response.status });
		}

		const data = await response.json();
		return json(data);
	} catch (err) {
		console.error('Error fetching checklists:', err);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};

export const POST: RequestHandler = async ({ request, fetch }) => {
	try {
		const body = await request.json();
		const apiUrl = `${BASE_API_URL}/audits/checklists/`;

		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: getHeadersWithCookies(request),
			body: JSON.stringify(body)
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			return json(errorData, { status: response.status });
		}

		const data = await response.json();
		return json(data, { status: 201 });
	} catch (err) {
		console.error('Error creating checklist:', err);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
