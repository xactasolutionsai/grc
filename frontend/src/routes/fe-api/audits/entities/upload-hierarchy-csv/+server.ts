import { BASE_API_URL } from '$lib/utils/constants';
import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Helper function to forward cookies
function getHeadersWithCookies(request: Request): Record<string, string> {
	const cookieHeader = request.headers.get('cookie');
	const headers: Record<string, string> = {};
	if (cookieHeader) {
		headers['Cookie'] = cookieHeader;
	}
	return headers;
}

export const POST: RequestHandler = async ({ fetch, request }) => {
	try {
		const formData = await request.formData();
		const apiUrl = `${BASE_API_URL}/audits/entities/upload-hierarchy-csv/`;

		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: getHeadersWithCookies(request),
			body: formData
		});

		if (!response.ok) {
			error(response.status, 'Failed to upload CSV');
		}

		const data = await response.json();

		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err) {
		console.error('Error uploading CSV:', err);
		error(500, 'Internal server error');
	}
};
