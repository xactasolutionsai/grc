import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
	try {
		const engagementId = params.id;

		// Load engagement data server-side if needed
		// This could include fetching the engagement details, permissions, etc.

		return {
			engagementId,
			title: 'Engagement Details'
		};
	} catch (error) {
		console.error('Error loading engagement data:', error);
		return {
			engagementId: params.id,
			title: 'Engagement Details'
		};
	}
};
