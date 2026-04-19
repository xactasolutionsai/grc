import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	// No data loading needed for the main page
	// The WorkpaperList component will handle data fetching client-side
	return {
		user: locals.user,
		title: 'Workpapers & Evidence'
	};
};

