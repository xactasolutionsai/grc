import { BASE_API_URL } from '$lib/utils/constants';
import { json } from '@sveltejs/kit';

const API_BASE = `${BASE_API_URL}/audits`;

export async function GET({ url, fetch, cookies }) {
    const searchParams = url.searchParams.toString();
    const apiUrl = `${API_BASE}/engagements/statistics/${searchParams ? '?' + searchParams : ''}`;
    const response = await fetch(apiUrl, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${cookies.get('authToken')}`
        }
    });
    const data = await response.json();
    return json(data, { status: response.status });
}
