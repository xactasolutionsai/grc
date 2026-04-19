import { BASE_API_URL } from '$lib/utils/constants';
import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ fetch, url }) => {
    try {
        const searchParams = url.searchParams.toString();
        const apiUrl = `${BASE_API_URL}/users/${searchParams ? '?' + searchParams : ''}`;

        const response = await fetch(apiUrl);

        if (!response.ok) {
            error(response.status, 'Failed to fetch users');
        }

        const data = await response.json();

        return new Response(JSON.stringify(data), {
            headers: {
                'Content-Type': 'application/json'
            }
        });
    } catch (err) {
        console.error('Error fetching users:', err);
        error(500, 'Internal server error');
    }
};
