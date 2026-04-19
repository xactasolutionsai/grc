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

export const GET: RequestHandler = async ({ fetch, params, request }) => {
	try {
		const apiUrl = `${BASE_API_URL}/workpapers/workpapers/${params.id}/approval_history/`;

		const response = await fetch(apiUrl, {
			headers: getHeadersWithCookies(request)
		});

		if (!response.ok) {
			error(response.status, 'Failed to fetch approval history');
		}

		const data = await response.json();

		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error fetching approval history:', err);
		error(500, 'Internal server error');
	}
};
