import { BASE_API_URL } from '$lib/utils/constants';
import { error } from '@sveltejs/kit';
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

export const POST: RequestHandler = async ({ fetch, request, params }) => {
	const path = params.path?.replace(/^\/+|\/+$/g, '') ?? '';
	if (!path) {
		error(400, 'Missing AI endpoint path');
	}

	let body: unknown = {};
	try {
		body = await request.json();
	} catch {
		body = {};
	}

	const apiUrl = `${BASE_API_URL}/ai/${path}/`;

	try {
		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: getHeadersWithCookies(request),
			body: JSON.stringify(body ?? {})
		});

		const text = await response.text();

		return new Response(text, {
			status: response.status,
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error calling AI endpoint:', err);
		error(502, 'AI proxy error');
	}
};
