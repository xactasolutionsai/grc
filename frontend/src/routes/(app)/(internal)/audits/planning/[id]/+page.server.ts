import type { PageServerLoad } from './$types';
import { BASE_API_URL } from '$lib/utils/constants';

export const load = (async ({ fetch, locals, params }) => {
	try {
		// Fetch the plan data to get the title
		const response = await fetch(`${BASE_API_URL}/audits/plans/${params.id}/`);
		if (response.ok) {
			const plan = await response.json();
			return {
				user: locals.user,
				planId: params.id,
				title: plan.title || 'Audit Plan Detail'
			};
		}
	} catch (error) {
		console.error('Error fetching plan title:', error);
	}

	// Fallback if plan fetch fails
	return {
		user: locals.user,
		planId: params.id,
		title: 'Audit Plan Detail'
	};
}) satisfies PageServerLoad;
