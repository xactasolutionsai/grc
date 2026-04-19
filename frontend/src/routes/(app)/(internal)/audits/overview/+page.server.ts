import { BASE_API_URL } from '$lib/utils/constants';
import type { PageServerLoad } from './$types';
import { m } from '$paraglide/messages';

export const load: PageServerLoad = async ({ fetch }) => {
	// Fetch dashboard metrics from backend
	const getDashboardMetrics = async () => {
		try {
			const response = await fetch(`${BASE_API_URL}/audits/engagements/dashboard-metrics/`);
			if (!response.ok) {
				console.error('Failed to fetch dashboard metrics:', response.statusText);
				return null;
			}
			const data = await response.json();
			return data;
		} catch (error) {
			console.error('Error fetching dashboard metrics:', error);
			return null;
		}
	};

	return {
		title: m.auditDashboard(),
		dashboardMetrics: await getDashboardMetrics()
	};
};
