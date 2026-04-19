<script lang="ts">
	import BarChart from '$lib/components/Chart/BarChart.svelte';

	interface Props {
		data: {
			labels: string[];
			values: Array<{ name: string; value: number }>;
		};
	}

	let { data }: Props = $props();

	// Extract estimated and actual values
	let estimatedHours = $derived(data.values[0]?.value || 0);
	let actualHours = $derived(data.values[1]?.value || 0);
	let budgetAllocated = $derived(data.values[2]?.value || 0);
	let actualCost = $derived(data.values[3]?.value || 0);
</script>

{#if data}
	<div class="space-y-8">
		<!-- Chart -->
		<div class="h-[320px] w-full mb-8">
			<BarChart
				name="budget-chart"
				labels={data.labels}
				values={data.values}
				height="h-[320px]"
				width="w-full"
			/>
		</div>

		<!-- Detailed Stats -->
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
			<div class="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg border border-blue-200 dark:border-blue-700">
				<div class="text-xs font-medium text-surface-600 dark:text-surface-400 mb-2">Estimated Hours</div>
				<div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
					{estimatedHours.toLocaleString()}
				</div>
			</div>
			<div class="p-4 bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-900/20 dark:to-indigo-800/20 rounded-lg border border-indigo-200 dark:border-indigo-700">
				<div class="text-xs font-medium text-surface-600 dark:text-surface-400 mb-2">Actual Hours</div>
				<div class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
					{actualHours.toLocaleString()}
				</div>
			</div>
			<div class="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg border border-green-200 dark:border-green-700">
				<div class="text-xs font-medium text-surface-600 dark:text-surface-400 mb-2">Budget Allocated</div>
				<div class="text-2xl font-bold text-green-600 dark:text-green-400">
					${budgetAllocated.toLocaleString()}
				</div>
			</div>
			<div class="p-4 bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20 rounded-lg border border-emerald-200 dark:border-emerald-700">
				<div class="text-xs font-medium text-surface-600 dark:text-surface-400 mb-2">Actual Cost</div>
				<div class="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
					${actualCost.toLocaleString()}
				</div>
			</div>
		</div>

		<!-- Variance Summary -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<div class="p-5 bg-white dark:bg-surface-900 rounded-xl border-2 {(actualHours - estimatedHours) > 0 ? 'border-error-300 dark:border-error-700' : 'border-success-300 dark:border-success-700'} shadow-sm">
				<div class="flex items-center justify-between">
					<div>
						<div class="text-sm font-medium text-surface-600 dark:text-surface-400 mb-1">Hours Variance</div>
						<div class="text-3xl font-bold {(actualHours - estimatedHours) > 0 ? 'text-error-600 dark:text-error-400' : 'text-success-600 dark:text-success-400'}">
							{#if estimatedHours > 0}
								{(actualHours - estimatedHours) > 0 ? '+' : ''}{Math.round(((actualHours - estimatedHours) / estimatedHours) * 100)}%
							{:else}
								N/A
							{/if}
						</div>
						<div class="text-xs text-surface-500 dark:text-surface-400 mt-1">
							{#if estimatedHours > 0}
								{(actualHours - estimatedHours) > 0 ? 'Over' : 'Under'} by {Math.abs(actualHours - estimatedHours).toLocaleString()} hours
							{/if}
						</div>
					</div>
					<div class="text-4xl {(actualHours - estimatedHours) > 0 ? 'text-error-600 dark:text-error-400' : 'text-success-600 dark:text-success-400'}">
						<i class="fa-solid {(actualHours - estimatedHours) > 0 ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down'}"></i>
					</div>
				</div>
			</div>
			<div class="p-5 bg-white dark:bg-surface-900 rounded-xl border-2 {(actualCost - budgetAllocated) > 0 ? 'border-error-300 dark:border-error-700' : 'border-success-300 dark:border-success-700'} shadow-sm">
				<div class="flex items-center justify-between">
					<div>
						<div class="text-sm font-medium text-surface-600 dark:text-surface-400 mb-1">Budget Variance</div>
						<div class="text-3xl font-bold {(actualCost - budgetAllocated) > 0 ? 'text-error-600 dark:text-error-400' : 'text-success-600 dark:text-success-400'}">
							{#if budgetAllocated > 0}
								{(actualCost - budgetAllocated) > 0 ? '+' : ''}{Math.round(((actualCost - budgetAllocated) / budgetAllocated) * 100)}%
							{:else}
								N/A
							{/if}
						</div>
						<div class="text-xs text-surface-500 dark:text-surface-400 mt-1">
							{#if budgetAllocated > 0}
								{(actualCost - budgetAllocated) > 0 ? 'Over' : 'Under'} by ${Math.abs(actualCost - budgetAllocated).toLocaleString()}
							{/if}
						</div>
					</div>
					<div class="text-4xl {(actualCost - budgetAllocated) > 0 ? 'text-error-600 dark:text-error-400' : 'text-success-600 dark:text-success-400'}">
						<i class="fa-solid {(actualCost - budgetAllocated) > 0 ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down'}"></i>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}
