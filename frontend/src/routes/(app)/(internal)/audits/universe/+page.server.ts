import type { PageServerLoad } from './$types';
import { m } from '$paraglide/messages';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		// Load audit entities via fe-api proxy
		const entitiesResponse = await fetch('/fe-api/audits/entities/');

		if (!entitiesResponse.ok) {
			console.warn('Failed to load audit entities:', entitiesResponse.status, entitiesResponse.statusText);
			return {
				entities: [],
				title: m.auditUniverse()
			};
		}

		const entities = await entitiesResponse.json();
		return {
			entities: entities.results || entities,
			title: m.auditUniverse()
		};
	} catch (error) {
		console.error('Error loading audit universe data:', error);
		return {
			entities: [],
			title: m.auditUniverse()
		};
	}
};
