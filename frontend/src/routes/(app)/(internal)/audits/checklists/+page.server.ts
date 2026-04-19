import type { PageServerLoad } from './$types';

export const load = (async ({ fetch, locals }) => {
	return {
		user: locals.user,
		title: 'Audit Checklists'
	};
}) satisfies PageServerLoad;
