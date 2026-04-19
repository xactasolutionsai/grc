import type { PageServerLoad } from './$types';

export const load = (async ({ params, locals }) => {
	return {
		checklistId: params.id,
		user: locals.user,
		title: 'Checklist Details'
	};
}) satisfies PageServerLoad;

