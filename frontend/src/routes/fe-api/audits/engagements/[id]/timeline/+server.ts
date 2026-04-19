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

export const GET: RequestHandler = async ({ params, fetch, request }) => {
    try {
        const apiUrl = `${BASE_API_URL}/audits/engagements/${params.id}/timeline/`;

        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: getHeadersWithCookies(request)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            return json({ error: errorData.detail || errorData.error || 'Failed to fetch timeline' }, { status: response.status });
        }

        const data = await response.json();
        return json(data, { status: response.status });
    } catch (err) {
        console.error('Error fetching timeline:', err);
        return json({ error: 'Internal server error' }, { status: 500 });
    }
};
