<script lang="ts">
	import { goto } from '$app/navigation';

	interface Engagement {
		id: number;
		title: string;
		status: string;
		priority: string;
		planned_start_date: string;
		planned_end_date: string;
		entity__name: string;
	}

	interface Props {
		engagements?: Engagement[];
	}

	let { engagements = [] }: Props = $props();

	// Status colors
	const statusColors: Record<string, string> = {
		draft: '#94a3b8',
		in_progress: '#3b82f6',
		fieldwork: '#f59e0b',
		review: '#8b5cf6',
		submitted: '#10b981',
		closed: '#6b7280',
		cancelled: '#ef4444'
	};

	// Priority indicators
	const priorityIcons: Record<string, string> = {
		low: 'fa-solid fa-circle text-success-500',
		medium: 'fa-solid fa-circle text-warning-500',
		high: 'fa-solid fa-circle text-error-500',
		critical: 'fa-solid fa-exclamation-circle text-error-600'
	};

	// Format date for display
	function formatDate(dateString: string): string {
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
	}

	// Calculate bar width based on duration
	function calculateWidth(startDate: string, endDate: string): number {
		const start = new Date(startDate);
		const end = new Date(endDate);
		const duration = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
		// Scale: 1 day = 2% width (max 100%)
		return Math.min(duration * 2, 100);
	}

	// Navigate to engagement detail
	function handleClick(id: number): void {
		goto(`/audits/engagements/${id}`);
	}
</script>

<div class="space-y-4">
	{#each engagements as engagement}
		<div class="group bg-white dark:bg-surface-900 p-4 rounded-lg border border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-md transition-all duration-200">
			<div class="flex items-start gap-3 mb-3">
				<div class="flex-shrink-0 mt-0.5">
					<i class="{priorityIcons[engagement.priority] || priorityIcons.medium}"></i>
				</div>
				<div class="flex-1 min-w-0">
					<button
						onclick={() => handleClick(engagement.id)}
						class="text-sm font-semibold text-surface-800 dark:text-surface-200 hover:text-primary-600 dark:hover:text-primary-400 cursor-pointer transition-colors block truncate text-left"
					>
						{engagement.title}
					</button>
					<div class="flex items-center gap-3 mt-1">
						<span class="text-xs text-surface-500 dark:text-surface-400 flex items-center gap-1">
							<i class="fa-solid fa-building text-[10px]"></i>
							{engagement.entity__name || 'No entity'}
						</span>
						<span class="text-xs text-surface-500 dark:text-surface-400 flex items-center gap-1">
							<i class="fa-solid fa-calendar text-[10px]"></i>
							{formatDate(engagement.planned_start_date)} - {formatDate(engagement.planned_end_date)}
						</span>
					</div>
				</div>
			</div>
			<div class="relative h-10 bg-gradient-to-r from-surface-100 to-surface-50 dark:from-surface-800 dark:to-surface-900 rounded-lg overflow-hidden shadow-inner border border-surface-200 dark:border-surface-700">
				<div
					class="absolute left-0 top-0 h-full rounded-lg transition-all duration-300 group-hover:shadow-lg flex items-center px-3 shadow-sm"
					style="width: {calculateWidth(engagement.planned_start_date, engagement.planned_end_date)}%; background: linear-gradient(135deg, {statusColors[engagement.status] || statusColors.draft}, {statusColors[engagement.status] || statusColors.draft}dd);"
				>
					<span class="text-xs font-semibold text-white drop-shadow-md truncate">
						{engagement.status.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
					</span>
				</div>
			</div>
		</div>
	{/each}
</div>

