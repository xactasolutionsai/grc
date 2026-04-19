import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	// Pass the workpaper ID to the page
	return {
		workpaperId: params.id,
		user: locals.user,
		title: 'Workpaper Details'
	};
};
