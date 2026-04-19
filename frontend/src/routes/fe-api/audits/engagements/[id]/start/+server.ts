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

export const POST: RequestHandler = async ({ params, fetch, request }) => {
    try {
        const apiUrl = `${BASE_API_URL}/audits/engagements/${params.id}/start/`;
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: getHeadersWithCookies(request)
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            return json({ error: errorData.detail || errorData.error || 'Failed to start engagement' }, { status: response.status });
        }
        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error starting engagement:', error);
        return json({ error: 'Internal server error' }, { status: 500 });
    }
};


