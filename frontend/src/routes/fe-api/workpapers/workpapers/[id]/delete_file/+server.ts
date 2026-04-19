import { BASE_API_URL } from '$lib/utils/constants';
import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

function getHeadersWithCookies(request: Request): Record<string, string> {
	const cookieHeader = request.headers.get('cookie');
	const headers: Record<string, string> = {};
	if (cookieHeader) {
		headers['Cookie'] = cookieHeader;
	}
	return headers;
}

export const DELETE: RequestHandler = async ({ fetch, params, request }) => {
	try {
		const apiUrl = `${BASE_API_URL}/workpapers/workpapers/${params.id}/delete_file/`;
		
		const response = await fetch(apiUrl, {
			method: 'DELETE',
			headers: getHeadersWithCookies(request),
		});
		
		if (!response.ok) {
			error(response.status, 'Failed to delete file');
		}
		
		const data = await response.json();
		
		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error deleting file:', err);
		error(500, 'Internal server error');
	}
};

