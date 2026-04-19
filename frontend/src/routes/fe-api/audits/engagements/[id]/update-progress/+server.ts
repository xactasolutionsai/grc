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

export const POST: RequestHandler = async ({ params, request, fetch }) => {
    try {
        const body = await request.json().catch(() => ({}));
        const apiUrl = `${BASE_API_URL}/audits/engagements/${params.id}/update-progress/`;
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: getHeadersWithCookies(request),
            body: JSON.stringify(body)
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            return json({ error: errorData.detail || errorData.error || 'Failed to update progress' }, { status: response.status });
        }
        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error updating progress:', error);
        return json({ error: 'Internal server error' }, { status: 500 });
    }
};
