import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
	return {
		user: locals.user,
		title: 'Create New Checklist'
	};
}) satisfies PageServerLoad;

