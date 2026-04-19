import type { PageServerLoad } from './$types';

export const load = (async ({ fetch, locals }) => {
	// This page doesn't need server-side data loading
	// All data is loaded client-side via the component
	return {
		user: locals.user,
		title: 'Audit Planning'
	};
}) satisfies PageServerLoad;
