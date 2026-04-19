import { BASE_API_URL } from '$lib/utils/constants';

import type { PageServerLoad } from './$types';

const nextMonth = (month: number): string => {
	if (month === 12) {
		return '01';
	}
	return (month + 1).toString().padStart(2, '0');
};

export const load = (async ({ fetch, locals, params }) => {
	const appliedControlsEndpoint = `${BASE_API_URL}/applied-controls/?eta__year=${params.year}&eta__month=${params.month}`;
	const riskAcceptancesEndpoint = `${BASE_API_URL}/risk-acceptances/?expiry_date__year=${params.year}&expiry_date__month=${params.month}`;
	const tasksEndpoint = `${BASE_API_URL}/task-templates/calendar/${params.year}-${params.month.padStart(2, '0')}-01/${nextMonth(parseInt(params.month)) === '01' ? parseInt(params.year) + 1 : params.year}-${nextMonth(parseInt(params.month))}-01`;
	const auditEntitiesEndpoint = `${BASE_API_URL}/audits/entities/?next_audit_date__year=${params.year}&next_audit_date__month=${params.month}`;
	const auditPlansEndpoint = `${BASE_API_URL}/audits/plans/?planned_start__year=${params.year}&planned_start__month=${params.month}`;

	const appliedControlsResponse = await fetch(appliedControlsEndpoint);
	const appliedControls = await appliedControlsResponse.json().then((res) => res.results);

	const riskAcceptancesResponse = await fetch(riskAcceptancesEndpoint);
	const riskAcceptances = await riskAcceptancesResponse.json().then((res) => res.results);

	const tasksResponse = await fetch(tasksEndpoint);
	const tasks = await tasksResponse.json();

	const auditEntitiesResponse = await fetch(auditEntitiesEndpoint);
	const auditEntities = await auditEntitiesResponse.json().then((res) => res.results);

	const auditPlansResponse = await fetch(auditPlansEndpoint);
	const auditPlans = await auditPlansResponse.json().then((res) => res.results);

	return {
		appliedControls,
		riskAcceptances,
		tasks,
		auditEntities,
		auditPlans,
		title: 'calendar'
	};
}) satisfies PageServerLoad;
