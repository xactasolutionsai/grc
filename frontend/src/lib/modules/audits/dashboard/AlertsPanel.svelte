<script lang="ts">
	import { goto } from '$app/navigation';
	
	interface Alert {
		overdue_engagements: Array<any>;
		never_audited_entities: Array<any>;
		budget_overruns: Array<any>;
		upcoming_deadlines: Array<any>;
	}
	
	interface Props {
		alerts?: Alert;
	}
	
	let { alerts }: Props = $props();
	
	function navigateToEngagement(id: number) {
		goto(`/audits/engagements/${id}`);
	}
	
	function navigateToEntity(id: number) {
		goto(`/audits/universe`);
	}
</script>

<!-- Alerts grid with 4 categories -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
	<!-- 1. Overdue Engagements -->
	<div class="card bg-white dark:bg-surface-900 p-6 rounded-xl border-l-4 border-error-500 shadow-lg">
		<h4 class="text-lg font-bold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
			<i class="fa-solid fa-exclamation-triangle text-error-500"></i>
			Overdue Engagements ({alerts?.overdue_engagements?.length || 0})
		</h4>
		{#if alerts?.overdue_engagements && alerts.overdue_engagements.length > 0}
			<div class="space-y-3 max-h-60 overflow-y-auto">
				{#each alerts.overdue_engagements as alert}
					<button
						onclick={() => navigateToEngagement(alert.id)}
						class="w-full text-left p-3 bg-error-50 dark:bg-error-900/20 rounded-lg hover:bg-error-100 dark:hover:bg-error-900/30 transition-colors"
					>
						<div class="font-semibold text-sm text-surface-900 dark:text-surface-50">{alert.title}</div>
						<div class="text-xs text-surface-600 dark:text-surface-400 mt-1">
							{alert.entity} • {alert.days_overdue} days overdue
						</div>
					</button>
				{/each}
			</div>
		{:else}
			<p class="text-sm text-surface-500">No overdue engagements</p>
		{/if}
	</div>

	<!-- 2. Never Audited Entities -->
	<div class="card bg-white dark:bg-surface-900 p-6 rounded-xl border-l-4 border-warning-500 shadow-lg">
		<h4 class="text-lg font-bold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
			<i class="fa-solid fa-flag text-warning-500"></i>
			Never Audited ({alerts?.never_audited_entities?.length || 0})
		</h4>
		{#if alerts?.never_audited_entities && alerts.never_audited_entities.length > 0}
			<div class="space-y-3 max-h-60 overflow-y-auto">
				{#each alerts.never_audited_entities as alert}
					<button
						onclick={() => navigateToEntity(alert.id)}
						class="w-full text-left p-3 bg-warning-50 dark:bg-warning-900/20 rounded-lg hover:bg-warning-100 dark:hover:bg-warning-900/30 transition-colors"
					>
						<div class="font-semibold text-sm text-surface-900 dark:text-surface-50">{alert.name}</div>
						<div class="text-xs text-surface-600 dark:text-surface-400 mt-1">
							{alert.criticality} Criticality • Risk: {alert.risk_score}
						</div>
					</button>
				{/each}
			</div>
		{:else}
			<p class="text-sm text-surface-500">All entities audited</p>
		{/if}
	</div>

	<!-- 3. Budget Overruns -->
	<div class="card bg-white dark:bg-surface-900 p-6 rounded-xl border-l-4 border-error-600 shadow-lg">
		<h4 class="text-lg font-bold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
			<i class="fa-solid fa-dollar-sign text-error-600"></i>
			Budget Overruns ({alerts?.budget_overruns?.length || 0})
		</h4>
		{#if alerts?.budget_overruns && alerts.budget_overruns.length > 0}
			<div class="space-y-3 max-h-60 overflow-y-auto">
				{#each alerts.budget_overruns as alert}
					<button
						onclick={() => navigateToEngagement(alert.id)}
						class="w-full text-left p-3 bg-error-50 dark:bg-error-900/20 rounded-lg hover:bg-error-100 dark:hover:bg-error-900/30 transition-colors"
					>
						<div class="font-semibold text-sm text-surface-900 dark:text-surface-50">{alert.title}</div>
						<div class="text-xs text-surface-600 dark:text-surface-400 mt-1">
							+{alert.variance_percent.toFixed(1)}% over budget
						</div>
					</button>
				{/each}
			</div>
		{:else}
			<p class="text-sm text-surface-500">No budget issues</p>
		{/if}
	</div>

	<!-- 4. Upcoming Deadlines -->
	<div class="card bg-white dark:bg-surface-900 p-6 rounded-xl border-l-4 border-primary-500 shadow-lg">
		<h4 class="text-lg font-bold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
			<i class="fa-solid fa-clock text-primary-500"></i>
			Upcoming Deadlines ({alerts?.upcoming_deadlines?.length || 0})
		</h4>
		{#if alerts?.upcoming_deadlines && alerts.upcoming_deadlines.length > 0}
			<div class="space-y-3 max-h-60 overflow-y-auto">
				{#each alerts.upcoming_deadlines as alert}
					<button
						onclick={() => navigateToEngagement(alert.id)}
						class="w-full text-left p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors"
					>
						<div class="font-semibold text-sm text-surface-900 dark:text-surface-50">{alert.title}</div>
						<div class="text-xs text-surface-600 dark:text-surface-400 mt-1">
							{alert.entity} • Due in {alert.days_remaining} days
						</div>
					</button>
				{/each}
			</div>
		{:else}
			<p class="text-sm text-surface-500">No upcoming deadlines</p>
		{/if}
	</div>
</div>

