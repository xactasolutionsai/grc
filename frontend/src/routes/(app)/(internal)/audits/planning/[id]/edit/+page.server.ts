import type { PageServerLoad } from './$types';

export const load = (async ({ fetch, locals, params }) => {
	// This page doesn't need server-side data loading
	// All data is loaded client-side via the component
	return {
		user: locals.user,
		planId: params.id,
		title: 'Edit Audit Plan'
	};
}) satisfies PageServerLoad;
