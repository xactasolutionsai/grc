import type { PageServerLoad } from './$types';

export const load = (async ({ params, locals }) => {
	return {
		checklistId: params.id,
		user: locals.user,
		title: 'Edit Checklist'
	};
}) satisfies PageServerLoad;

