import type { PageServerLoad } from './$types';

export const load = (async ({ fetch, locals, params }) => {
	return {
		user: locals.user,
		title: 'Checklist Execution',
		executionId: params.id
	};
}) satisfies PageServerLoad;

