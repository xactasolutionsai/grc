import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		// Load any server-side data needed for the engagements page
		// This could include user permissions, initial data, etc.
		return {
			title: 'Audit Engagements'
		};
	} catch (error) {
		console.error('Error loading audit engagements data:', error);
		return {
			title: 'Audit Engagements'
		};
	}
};
