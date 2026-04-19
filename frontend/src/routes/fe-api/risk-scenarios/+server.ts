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

export const GET: RequestHandler = async ({ url, fetch, request }) => {
	try {
		const searchParams = url.searchParams.toString();
		const apiUrl = `${BASE_API_URL}/risk-scenarios/${searchParams ? '?' + searchParams : ''}`;
		
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
		console.error('Error fetching risk scenarios:', err);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};

