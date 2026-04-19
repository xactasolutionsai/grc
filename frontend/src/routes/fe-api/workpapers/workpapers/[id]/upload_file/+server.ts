import { BASE_API_URL } from '$lib/utils/constants';
import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ params, request, cookies }) => {
	try {
		const formData = await request.formData();
		const apiUrl = `${BASE_API_URL}/workpapers/workpapers/${params.id}/upload_file/`;
		
		console.log('[fe-api] Uploading file for workpaper:', params.id);
		console.log('[fe-api] API URL:', apiUrl);
		
		// Get authentication cookies
		const sessionid = cookies.get('sessionid');
		const csrftoken = cookies.get('csrftoken');
		
		// Don't set Content-Type header - let fetch set it automatically with boundary
		const headers: Record<string, string> = {};
		if (sessionid) {
			headers['Cookie'] = `sessionid=${sessionid}${csrftoken ? `; csrftoken=${csrftoken}` : ''}`;
		}
		if (csrftoken) {
			headers['X-CSRFToken'] = csrftoken;
		}
		
		console.log('[fe-api] Sending request to backend...');
		
		// Use native fetch with proper FormData handling
		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: headers,
			body: formData,
			// @ts-ignore - duplex is needed for streaming FormData
			duplex: 'half'
		});
		
		console.log('[fe-api] Response status:', response.status);
		
		if (!response.ok) {
			const errorText = await response.text();
			console.error('[fe-api] Backend error:', errorText);
			error(response.status, `Failed to upload file: ${errorText}`);
		}
		
		const data = await response.json();
		console.log('[fe-api] Upload successful');
		
		return new Response(JSON.stringify(data), {
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (err: any) {
		console.error('[fe-api] Exception:', err);
		error(500, `Internal server error: ${err?.message || 'Unknown error'}`);
	}
};

