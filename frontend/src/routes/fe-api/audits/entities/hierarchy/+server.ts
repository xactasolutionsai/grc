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

export const GET: RequestHandler = async ({ fetch, url, request }) => {
	try {
		const searchParams = url.searchParams.toString();
		const apiUrl = `${BASE_API_URL}/audits/entities/hierarchy/${searchParams ? '?' + searchParams : ''}`;
		
		const response = await fetch(apiUrl, {
			headers: getHeadersWithCookies(request)
		});
		
		if (!response.ok) {
			error(response.status, 'Failed to fetch hierarchy');
		}
		
		const data = await response.json();
		
		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error fetching hierarchy:', err);
		error(500, 'Internal server error');
	}
};

