<script lang="ts">
	import { Tabs } from '@skeletonlabs/skeleton-svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import DonutChart from '$lib/components/Chart/DonutChart.svelte';
	import BarChart from '$lib/components/Chart/BarChart.svelte';
	import TreemapChart from '$lib/components/Chart/TreemapChart.svelte';
	import SimpleCard from '$lib/components/DataViz/SimpleCard.svelte';
	import CardGroup from '$lib/components/DataViz/CardGroup.svelte';
	import LoadingSpinner from '$lib/components/utils/LoadingSpinner.svelte';
	import EntityCoverageHeatmap from '$lib/modules/audits/dashboard/EntityCoverageHeatmap.svelte';
	import TimelineChart from '$lib/modules/audits/dashboard/TimelineChart.svelte';
	import BudgetComparisonChart from '$lib/modules/audits/dashboard/BudgetComparisonChart.svelte';
	import AlertsPanel from '$lib/modules/audits/dashboard/AlertsPanel.svelte';
	import CompletionTrendChart from '$lib/modules/audits/dashboard/CompletionTrendChart.svelte';
	import { 
		transformStatusData, 
		transformPriorityData, 
		transformAuditTypeData,
		transformChecklistExecutionData,
		transformChecklistResultsData,
		transformBudgetData
	} from '$lib/modules/audits/dashboard/api.js';
	import { m } from '$paraglide/messages';
	import type { PageData } from './$types';

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();

	// Tab state management
	let activeTab = $derived(page.url.searchParams.get('tab') || 'overview');
	
	function handleTabChange(tabValue: string): void {
		page.url.searchParams.set('tab', tabValue);
		goto(page.url);
	}
	
	// Click handlers for drill-down navigation
	function handleStatusClick(statusLabel: string): void {
		const statusMap: Record<string, string> = {
			'Draft': 'draft',
			'In Progress': 'in_progress',
			'Fieldwork': 'fieldwork',
			'Review': 'review',
			'Submitted': 'submitted',
			'Closed': 'closed',
			'Cancelled': 'cancelled'
		};
		const statusValue = statusMap[statusLabel];
		if (statusValue) {
			goto(`/audits/engagements?status=${statusValue}`);
		}
	}
	
	function handlePriorityClick(priorityLabel: string): void {
		const priorityMap: Record<string, string> = {
			'Low': 'low',
			'Medium': 'medium',
			'High': 'high',
			'Critical': 'critical'
		};
		const priorityValue = priorityMap[priorityLabel];
		if (priorityValue) {
			goto(`/audits/engagements?priority=${priorityValue}`);
		}
	}

	// Transform data for charts
	let statusChartData = $derived(
		data.dashboardMetrics?.status_distribution 
			? transformStatusData(data.dashboardMetrics.status_distribution)
			: null
	);

	let priorityChartData = $derived(
		data.dashboardMetrics?.priority_distribution
			? transformPriorityData(data.dashboardMetrics.priority_distribution)
			: null
	);

	let auditTypeChartData: { labels: string[]; values: Array<{ name: string; value: number }> } | null = $derived(
		data.dashboardMetrics?.audit_type_distribution
			? transformAuditTypeData(data.dashboardMetrics.audit_type_distribution) as { labels: string[]; values: Array<{ name: string; value: number }> }
			: null
	);

	let checklistExecutionData: Array<{ name: string; value: number }> | null = $derived(
		data.dashboardMetrics?.checklist_stats
			? transformChecklistExecutionData(data.dashboardMetrics.checklist_stats)
			: null
	);

	let checklistResultsData: Array<{ name: string; value: number }> | null = $derived(
		data.dashboardMetrics?.checklist_results
			? transformChecklistResultsData(data.dashboardMetrics.checklist_results)
			: null
	);

	let budgetChartData: { labels: string[]; values: Array<{ name: string; value: number }> } | null = $derived(
		data.dashboardMetrics?.budget_stats
			? transformBudgetData(data.dashboardMetrics.budget_stats) as { labels: string[]; values: Array<{ name: string; value: number }> }
			: null
	);
</script>

<div class="px-4 pb-8 space-y-6">
	{#if !data.dashboardMetrics}
		<div class="flex items-center justify-center py-20">
			<div class="text-center space-y-4">
				<LoadingSpinner />
				<p class="text-surface-600">Loading dashboard...</p>
			</div>
		</div>
	{:else}
		<Tabs value={activeTab} onValueChange={(e) => handleTabChange(e.value)}>
			{#snippet list()}
				<div class="bg-white dark:bg-surface-800 rounded-lg shadow-sm p-1 flex gap-1 border border-surface-200 dark:border-surface-700">
					<Tabs.Control value="overview">
						<i class="fa-solid fa-chart-pie mr-2"></i>
						{m.overview()}
					</Tabs.Control>
					<Tabs.Control value="tracking">
						<i class="fa-solid fa-tasks mr-2"></i>
						Engagement Tracking
					</Tabs.Control>
					<Tabs.Control value="coverage">
						<i class="fa-solid fa-shield-halved mr-2"></i>
						Coverage & Risk
					</Tabs.Control>
					<Tabs.Control value="quality">
						<i class="fa-solid fa-check-circle mr-2"></i>
						Quality & Results
					</Tabs.Control>
				</div>
			{/snippet}
			{#snippet content()}
				{#key activeTab}
					<div class="mt-6">
						<!-- Tab 1: Overview -->
						<Tabs.Panel value="overview">
							<div class="space-y-6">
								<!-- Core Metrics Cards -->
								<CardGroup title="Core Metrics" icon="fa-solid fa-gauge-high">
									<SimpleCard
										count={String(data.dashboardMetrics.core_metrics.total)}
										label="Total Engagements"
										href="/audits/engagements"
									/>
									<SimpleCard
										count={String(data.dashboardMetrics.core_metrics.overdue)}
										label="Overdue"
										href="/audits/engagements?status=overdue"
										emphasis={true}
									/>
									<SimpleCard
										count={String(data.dashboardMetrics.core_metrics.completed_this_month)}
										label="Completed This Month"
										href="/audits/engagements?status=closed"
									/>
									<SimpleCard
										count={String(data.dashboardMetrics.core_metrics.in_progress)}
										label="In Progress"
										href="/audits/engagements?status=in_progress"
									/>
								</CardGroup>

							<!-- Alerts & Notifications -->
							{#if data.dashboardMetrics?.alerts}
								<div class="mt-8">
									<h3 class="text-xl font-bold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
										<i class="fa-solid fa-bell text-error-500"></i>
										Alerts & Notifications
									</h3>
									<AlertsPanel alerts={data.dashboardMetrics.alerts} />
								</div>
							{/if}

							<!-- Status and Priority Charts -->
							<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
								<!-- Engagement Status -->
								<div class="card bg-white dark:bg-surface-800 p-6 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700">
									<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
										<i class="fa-solid fa-clipboard-list text-primary-600"></i>
										Engagement Status
									</h3>
									{#if statusChartData}
										<div class="h-[400px] w-full">
											<DonutChart 
												name="status-chart" 
												values={statusChartData}
												height="h-[400px]"
												width="w-full"
												onSegmentClick={(label) => handleStatusClick(label)}
											/>
										</div>
									{:else}
										<div class="flex items-center justify-center h-64 text-surface-400">
											<div class="text-center">
												<i class="fa-solid fa-inbox text-4xl mb-2"></i>
												<p>No data available</p>
											</div>
										</div>
									{/if}
								</div>

								<!-- Priority Breakdown -->
								<div class="card bg-white dark:bg-surface-800 p-6 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700">
									<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
										<i class="fa-solid fa-exclamation-triangle text-warning-600"></i>
										Priority Breakdown
									</h3>
									{#if priorityChartData}
										<div class="h-[400px] w-full">
											<DonutChart 
												name="priority-chart" 
												values={priorityChartData}
												height="h-[400px]"
												width="w-full"
												onSegmentClick={(label) => handlePriorityClick(label)}
											/>
										</div>
									{:else}
										<div class="flex items-center justify-center h-64 text-surface-400">
											<div class="text-center">
												<i class="fa-solid fa-inbox text-4xl mb-2"></i>
												<p>No data available</p>
											</div>
										</div>
									{/if}
								</div>
							</div>
							</div>
						</Tabs.Panel>

						<!-- Tab 2: Engagement Tracking -->
						<Tabs.Panel value="tracking">
							<div class="space-y-6">
								<!-- Audit Type Distribution -->
								<div class="card bg-white dark:bg-surface-800 p-6 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700">
									<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
										<i class="fa-solid fa-layer-group text-primary-600"></i>
										Audit Type Distribution
									</h3>
									{#if auditTypeChartData}
										<div class="h-[350px] w-full">
											<BarChart 
												name="audit-type-chart" 
												labels={auditTypeChartData.labels} 
												values={auditTypeChartData.values}
												height="h-[350px]"
												width="w-full"
											/>
										</div>
									{:else}
										<div class="flex items-center justify-center h-64 text-surface-400">
											<div class="text-center">
												<i class="fa-solid fa-inbox text-4xl mb-2"></i>
												<p>No data available</p>
											</div>
										</div>
									{/if}
								</div>

								<!-- Timeline View -->
								<div class="card bg-white dark:bg-surface-800 p-6 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700">
									<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
										<i class="fa-solid fa-calendar-days text-primary-600"></i>
										Upcoming Engagements (Next 90 Days)
									</h3>
									{#if data.dashboardMetrics.upcoming_engagements && data.dashboardMetrics.upcoming_engagements.length > 0}
										<TimelineChart engagements={data.dashboardMetrics.upcoming_engagements} />
									{:else}
										<div class="flex items-center justify-center h-64 text-surface-400">
											<div class="text-center">
												<i class="fa-solid fa-calendar-xmark text-4xl mb-2"></i>
												<p>No upcoming engagements</p>
											</div>
										</div>
									{/if}
								</div>

								<!-- Budget vs Actual -->
								<div class="card bg-white dark:bg-surface-800 p-6 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700">
									<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
										<i class="fa-solid fa-dollar-sign text-success-600"></i>
										Budget vs Actual
									</h3>
									{#if budgetChartData}
										<div class="w-full">
											<BudgetComparisonChart data={budgetChartData} />
										</div>
									{:else}
										<div class="flex items-center justify-center h-64 text-surface-400">
											<div class="text-center">
												<i class="fa-solid fa-inbox text-4xl mb-2"></i>
												<p>No data available</p>
											</div>
										</div>
									{/if}
								</div>
								
								<!-- Completion Trend -->
								<div class="card bg-white dark:bg-surface-800 p-6 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700">
									<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
										<i class="fa-solid fa-chart-line text-success-600"></i>
										Completion Trend (12 Months)
									</h3>
									{#if data.dashboardMetrics?.completion_trend}
										<div class="h-[400px] w-full">
											<CompletionTrendChart data={data.dashboardMetrics.completion_trend} />
										</div>
									{:else}
										<div class="flex items-center justify-center h-64 text-surface-400">
											<div class="text-center">
												<i class="fa-solid fa-inbox text-4xl mb-2"></i>
												<p>No trend data available</p>
											</div>
										</div>
									{/if}
								</div>
							</div>
						</Tabs.Panel>

						<!-- Tab 3: Coverage & Risk -->
						<Tabs.Panel value="coverage">
							<div class="space-y-6">
								<!-- Entity Coverage Heatmap -->
								<div class="card bg-white dark:bg-surface-800 p-6 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700">
									<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
										<i class="fa-solid fa-th text-primary-600"></i>
										Entity Coverage Heatmap
									</h3>
									<p class="text-sm text-surface-600 dark:text-surface-400 mb-6">
										Entity Type vs Criticality - Color indicates audit status
									</p>
									{#if data.dashboardMetrics.entity_coverage.coverage_matrix.length > 0}
										<div class="bg-surface-50 dark:bg-surface-900 p-4 rounded-lg">
											<EntityCoverageHeatmap matrix={data.dashboardMetrics.entity_coverage.coverage_matrix} />
										</div>
									{:else}
										<div class="flex items-center justify-center h-64 text-surface-400">
											<div class="text-center">
												<i class="fa-solid fa-building text-4xl mb-2"></i>
												<p>No entities available</p>
											</div>
										</div>
									{/if}
								</div>

								<!-- Entity Risk Distribution -->
								<div class="card bg-white dark:bg-surface-800 p-6 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700">
									<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
										<i class="fa-solid fa-chart-area text-error-600"></i>
										Entity Risk Distribution
									</h3>
									<p class="text-sm text-surface-600 dark:text-surface-400 mb-4">
										Top 50 entities by risk score
									</p>
									{#if data.dashboardMetrics.entity_risk_data.length > 0}
										<div class="h-[450px] w-full">
											<TreemapChart 
												name="entity-risk-treemap"
												tree={data.dashboardMetrics.entity_risk_data}
												height="h-[450px]"
												width="w-full"
											/>
										</div>
									{:else}
										<div class="flex items-center justify-center h-64 text-surface-400">
											<div class="text-center">
												<i class="fa-solid fa-shield-halved text-4xl mb-2"></i>
												<p>No risk data available</p>
											</div>
										</div>
									{/if}
								</div>
							</div>
						</Tabs.Panel>

						<!-- Tab 4: Quality & Results -->
						<Tabs.Panel value="quality">
							<div class="space-y-6">
								<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
									<!-- Checklist Execution Progress -->
									<div class="card bg-white dark:bg-surface-800 p-6 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700">
										<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
											<i class="fa-solid fa-list-check text-primary-600"></i>
											Checklist Execution Status
										</h3>
										{#if checklistExecutionData}
											<div class="h-[350px] w-full">
												<DonutChart 
													name="checklist-execution-chart" 
													values={checklistExecutionData}
													height="h-[350px]"
													width="w-full"
												/>
											</div>
										{:else}
											<div class="flex items-center justify-center h-64 text-surface-400">
												<div class="text-center">
													<i class="fa-solid fa-inbox text-4xl mb-2"></i>
													<p>No data available</p>
												</div>
											</div>
										{/if}
									</div>

									<!-- Checklist Results -->
									<div class="card bg-white dark:bg-surface-800 p-6 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700">
										<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
											<i class="fa-solid fa-check-double text-success-600"></i>
											Checklist Test Results
										</h3>
										{#if checklistResultsData}
											<div class="h-[350px] w-full">
												<DonutChart 
													name="checklist-results-chart" 
													values={checklistResultsData}
													height="h-[350px]"
													width="w-full"
												/>
											</div>
										{:else}
											<div class="flex items-center justify-center h-64 text-surface-400">
												<div class="text-center">
													<i class="fa-solid fa-inbox text-4xl mb-2"></i>
													<p>No data available</p>
												</div>
											</div>
										{/if}
									</div>
								</div>

								<!-- Performance Metrics -->
								<div class="card bg-white dark:bg-surface-800 p-6 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700">
									<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-6 flex items-center gap-2">
										<i class="fa-solid fa-chart-line text-primary-600"></i>
										Performance Metrics
									</h3>
									<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
										<div class="text-center p-6 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-xl border border-primary-200 dark:border-primary-700 shadow-sm hover:shadow-md transition-shadow">
											<div class="text-4xl font-bold text-primary-600 dark:text-primary-400 mb-3">
												{Math.round(data.dashboardMetrics.performance_metrics.avg_duration_days)}
											</div>
											<div class="text-sm font-medium text-surface-700 dark:text-surface-300">
												Avg Duration (Days)
											</div>
										</div>
										<div class="text-center p-6 bg-gradient-to-br from-success-50 to-success-100 dark:from-success-900/20 dark:to-success-800/20 rounded-xl border border-success-200 dark:border-success-700 shadow-sm hover:shadow-md transition-shadow">
											<div class="text-4xl font-bold text-success-600 dark:text-success-400 mb-3">
												{Math.round(data.dashboardMetrics.performance_metrics.on_time_completion_rate)}%
											</div>
											<div class="text-sm font-medium text-surface-700 dark:text-surface-300">
												On-Time Completion
											</div>
										</div>
										<div class="text-center p-6 bg-gradient-to-br {data.dashboardMetrics.performance_metrics.budget_variance_percent > 0 ? 'from-error-50 to-error-100 dark:from-error-900/20 dark:to-error-800/20 border-error-200 dark:border-error-700' : 'from-success-50 to-success-100 dark:from-success-900/20 dark:to-success-800/20 border-success-200 dark:border-success-700'} rounded-xl border shadow-sm hover:shadow-md transition-shadow">
											<div class="text-4xl font-bold {data.dashboardMetrics.performance_metrics.budget_variance_percent > 0 ? 'text-error-600 dark:text-error-400' : 'text-success-600 dark:text-success-400'} mb-3">
												{data.dashboardMetrics.performance_metrics.budget_variance_percent > 0 ? '+' : ''}{Math.round(data.dashboardMetrics.performance_metrics.budget_variance_percent)}%
											</div>
											<div class="text-sm font-medium text-surface-700 dark:text-surface-300">
												Budget Variance
											</div>
										</div>
									</div>
								</div>
							</div>
						</Tabs.Panel>
					</div>
				{/key}
			{/snippet}
		</Tabs>
	{/if}
</div>
