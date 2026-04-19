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
		const apiUrl = `${BASE_API_URL}/audits/checklist-executions/${params.id}/summary/`;

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
		console.error('Error fetching summary:', err);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
