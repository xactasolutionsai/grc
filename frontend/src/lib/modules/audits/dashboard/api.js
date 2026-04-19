import { BASE_API_URL } from '$lib/utils/constants';

/**
 * Fetch comprehensive dashboard metrics from the backend
 * @returns {Promise<Object>} Dashboard metrics data
 */
export async function getDashboardMetrics() {
	const response = await fetch(`${BASE_API_URL}/audits/engagements/dashboard-metrics/`);
	if (!response.ok) {
		throw new Error(`Failed to fetch dashboard metrics: ${response.statusText}`);
	}
	const data = await response.json();
	return data;
}

/**
 * Transform status distribution data for donut chart
 * @param {Object} statusDistribution - Status distribution from API
 * @returns {Array} Chart data with name and value
 */
export function transformStatusData(statusDistribution) {
	const values = [];
	const colors = {
		draft: '#94a3b8',
		in_progress: '#3b82f6',
		fieldwork: '#f59e0b',
		review: '#8b5cf6',
		submitted: '#10b981',
		closed: '#6b7280',
		cancelled: '#ef4444'
	};

	Object.entries(statusDistribution).forEach(([key, data]) => {
		values.push({
			name: data.label,
			value: data.count,
			itemStyle: { color: colors[key] || '#64748b' }
		});
	});

	return values;
}

/**
 * Transform priority distribution data for donut chart
 * @param {Object} priorityDistribution - Priority distribution from API
 * @returns {Array} Chart data with name and value
 */
export function transformPriorityData(priorityDistribution) {
	const values = [];
	const colors = {
		low: '#10b981',
		medium: '#f59e0b',
		high: '#f97316',
		critical: '#ef4444'
	};

	Object.entries(priorityDistribution).forEach(([key, data]) => {
		values.push({
			name: data.label,
			value: data.count,
			itemStyle: { color: colors[key] || '#64748b' }
		});
	});

	return values;
}

/**
 * Transform audit type distribution for bar chart
 * @param {Object} auditTypeDistribution - Audit type distribution from API
 * @returns {Object} Chart data with labels and values
 */
export function transformAuditTypeData(auditTypeDistribution) {
	const labels = [];
	const values = [];

	Object.entries(auditTypeDistribution).forEach(([key, data]) => {
		labels.push(data.label);
		values.push({
			name: data.label,
			value: data.count
		});
	});

	return { labels, values };
}

/**
 * Transform checklist execution status for donut chart
 * @param {Object} checklistStats - Checklist statistics from API
 * @returns {Array} Chart data with name and value
 */
export function transformChecklistExecutionData(checklistStats) {
	const values = [];
	const colors = {
		not_started: '#94a3b8',
		in_progress: '#f59e0b',
		completed: '#10b981'
	};

	if (checklistStats.by_status) {
		Object.entries(checklistStats.by_status).forEach(([key, data]) => {
			values.push({
				name: data.label,
				value: data.count,
				itemStyle: { color: colors[key] || '#64748b' }
			});
		});
	}

	return values;
}

/**
 * Transform checklist results for donut chart
 * @param {Object} checklistResults - Checklist results from API
 * @returns {Array} Chart data with name and value
 */
export function transformChecklistResultsData(checklistResults) {
	const values = [];
	const colors = {
		not_tested: '#94a3b8',
		pass: '#10b981',
		fail: '#ef4444',
		needs_followup: '#f59e0b',
		not_applicable: '#6b7280'
	};

	if (checklistResults.by_result) {
		Object.entries(checklistResults.by_result).forEach(([key, data]) => {
			values.push({
				name: data.label,
				value: data.count,
				itemStyle: { color: colors[key] || '#64748b' }
			});
		});
	}

	return values;
}

/**
 * Transform budget data for comparison chart
 * @param {Object} budgetStats - Budget statistics from API
 * @returns {Object} Chart data comparing estimated vs actual
 */
export function transformBudgetData(budgetStats) {
	return {
		labels: ['Hours', 'Budget'],
		values: [
			{
				name: 'Estimated Hours',
				value: budgetStats.total_estimated_hours || 0
			},
			{
				name: 'Actual Hours',
				value: budgetStats.total_actual_hours || 0
			},
			{
				name: 'Budget Allocated',
				value: budgetStats.total_budget_allocated || 0
			},
			{
				name: 'Actual Cost',
				value: budgetStats.total_actual_cost || 0
			}
		]
	};
}

/**
 * Get color based on audit status
 * @param {number} current - Number of current audits
 * @param {number} dueSoon - Number of due soon
 * @param {number} overdue - Number of overdue
 * @param {number} neverAudited - Number never audited
 * @returns {string} Color code for the cell
 */
export function getCoverageColor(current, dueSoon, overdue, neverAudited) {
	const total = current + dueSoon + overdue + neverAudited;
	if (total === 0) return '#f1f5f9'; // Very light gray for empty
	
	if (overdue > 0 || neverAudited > 0) {
		// Red if any overdue or never audited
		const severity = (overdue + neverAudited) / total;
		if (severity > 0.5) return '#ef4444'; // Strong red
		return '#f87171'; // Light red
	}
	
	if (dueSoon > 0) {
		// Yellow if due soon
		const urgency = dueSoon / total;
		if (urgency > 0.5) return '#f59e0b'; // Strong yellow
		return '#fbbf24'; // Light yellow
	}
	
	// Green if all current
	return '#10b981';
}

