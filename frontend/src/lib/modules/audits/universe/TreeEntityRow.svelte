<script lang="ts">
	import { deleteEntity } from './api.js';
	import Self from './TreeEntityRow.svelte';

	interface Props {
		node: any;
		level: number;
	}

	let { node, level = 0 }: Props = $props();
	
	let deleting = $state(false);
	let isExpanded = $state(true); // Start expanded by default

	function formatEntityType(type: string) {
		return type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
	}

	function formatDate(dateString: string | null) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleDateString();
	}

	function formatDateTime(dateString: string | null) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleString();
	}

	async function handleDelete() {
		if (!confirm(`Are you sure you want to delete "${node.name}"? This action cannot be undone.`)) {
			return;
		}

		try {
			deleting = true;
			await deleteEntity(node.id);
			// Dispatch event to parent to refresh the list
			window.dispatchEvent(new CustomEvent('entityDeleted', { detail: { id: node.id } }));
		} catch (error) {
			console.error('Error deleting entity:', error);
			alert('Failed to delete entity. Please try again.');
		} finally {
			deleting = false;
		}
	}

	function viewInCalendar(dateString: string) {
		const date = new Date(dateString);
		const year = date.getFullYear();
		const month = date.getMonth() + 1; // JavaScript months are 0-based
		window.location.href = `/calendar/${year}/${month}`;
	}

	function toggleExpanded() {
		if (node.children && node.children.length > 0) {
			isExpanded = !isExpanded;
		}
	}

	// Entity type icons
	const typeIcons: Record<string, string> = {
		business_unit: '🏢',
		division: '🔷',
		function: '⚙️',
		section: '📑',
		unit: '📦',
		process: '🔄',
		system: '💻',
		vendor: '🤝',
		compliance_domain: '📋',
		audit_domain: '🎯'
	};

	// Priority colors
	const priorityColors: Record<string, { bg: string; text: string; icon: string }> = {
		critical: { bg: 'bg-error-100 dark:bg-error-900/30', text: 'text-error-800 dark:text-error-200', icon: '🔴' },
		high: { bg: 'bg-warning-100 dark:bg-warning-900/30', text: 'text-warning-800 dark:text-warning-200', icon: '🟠' },
		medium: { bg: 'bg-warning-100 dark:bg-warning-900/30', text: 'text-warning-800 dark:text-warning-200', icon: '🟡' },
		low: { bg: 'bg-success-100 dark:bg-success-900/30', text: 'text-success-800 dark:text-success-200', icon: '🟢' }
	};
</script>

<div 
	class="entity-card transition-all duration-200"
	style="margin-left: {level * 2}rem"
>
	<!-- Main Card -->
	<div class="bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg shadow-sm hover:shadow-md transition-all duration-200">
		<!-- Card Header - Always Visible -->
		<div class="p-4">
			<div class="flex items-center justify-between gap-4">
				<!-- Left Section: Expand Button + Entity Info -->
				<div class="flex items-center gap-3 flex-1 min-w-0">
					<!-- Expand/Collapse Button -->
					{#if node.children && node.children.length > 0}
						<button
							onclick={toggleExpanded}
							class="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-md hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
							aria-label={isExpanded ? 'Collapse' : 'Expand'}
						>
							<svg 
								class="w-4 h-4 text-surface-600 dark:text-surface-300 transition-transform duration-200 {isExpanded ? 'rotate-90' : ''}"
								fill="none" 
								stroke="currentColor" 
								viewBox="0 0 24 24"
							>
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
							</svg>
						</button>
					{:else}
						<div class="w-6"></div>
					{/if}

					<!-- Entity Type Icon -->
					<div class="flex-shrink-0 text-2xl">
						{typeIcons[node.entity_type] || '📄'}
					</div>

					<!-- Entity Name & Description -->
					<div class="flex-1 min-w-0">
						<div class="flex items-center gap-2 flex-wrap">
							<h3 class="text-base font-semibold text-surface-900 dark:text-surface-50 truncate">
								{node.name}
							</h3>
							{#if node.children && node.children.length > 0}
								<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-surface-100 dark:bg-surface-700 text-surface-600 dark:text-surface-300">
									{node.children.length} {node.children.length === 1 ? 'child' : 'children'}
								</span>
							{/if}
						</div>
						{#if node.description}
							<p class="text-sm text-surface-600 dark:text-surface-400 truncate mt-0.5">
								{node.description}
							</p>
						{/if}
					</div>
				</div>

				<!-- Middle Section: Badges -->
				<div class="flex items-center gap-2 flex-wrap">
					<!-- Type Badge -->
					<span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-200">
						{formatEntityType(node.entity_type)}
					</span>

					<!-- Priority Badge -->
					{#if node.priority}
						<span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium {priorityColors[node.priority]?.bg} {priorityColors[node.priority]?.text}">
							{priorityColors[node.priority]?.icon} {node.priority.charAt(0).toUpperCase() + node.priority.slice(1)}
						</span>
					{/if}

					<!-- Status Badge -->
					<span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium {node.is_active ? 'bg-success-100 dark:bg-success-900/30 text-success-800 dark:text-success-200' : 'bg-error-100 dark:bg-error-900/30 text-error-800 dark:text-error-200'}">
						{node.is_active ? '✅ Active' : '⏸️ Inactive'}
					</span>

					<!-- Location Badge -->
					{#if node.full_location}
						<span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200">
							📍 {node.full_location}
						</span>
					{:else if node.location}
						<span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-surface-100 dark:bg-surface-700 text-surface-700 dark:text-surface-300">
							📍 {node.location}
						</span>
					{/if}
				</div>

				<!-- Right Section: Actions -->
				<div class="flex items-center gap-1 flex-shrink-0">
					<a
						href="/audits/universe/{node.id}"
						class="p-2 text-surface-600 dark:text-surface-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-surface-100 dark:hover:bg-surface-700 rounded-lg transition-colors"
						title="View details"
						aria-label="View details for {node.name}"
						data-testid="tablerow-detail-button"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
						</svg>
					</a>

					{#if node.next_audit_date}
						<button
							onclick={() => viewInCalendar(node.next_audit_date)}
							class="p-2 text-surface-600 dark:text-surface-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-surface-100 dark:hover:bg-surface-700 rounded-lg transition-colors"
							title="View in Calendar"
							aria-label="View {node.name} in Calendar"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
							</svg>
						</button>
					{/if}

					<a
						href="/audits/planning/new?entity={node.id}"
						class="p-2 text-surface-600 dark:text-surface-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-surface-100 dark:hover:bg-surface-700 rounded-lg transition-colors"
						title="Plan Audit"
						aria-label="Plan audit for {node.name}"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
					</a>

					<button
						onclick={handleDelete}
						disabled={deleting}
						class="p-2 text-surface-600 dark:text-surface-300 hover:text-error-600 dark:hover:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/20 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
						title="Delete entity"
						data-testid="tablerow-delete-button"
					>
						{#if deleting}
							<svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
						{:else}
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
							</svg>
						{/if}
					</button>
				</div>
			</div>

			<!-- Additional Info Row -->
			<div class="mt-3 flex items-center gap-4 text-xs text-surface-500 dark:text-surface-400 flex-wrap">
				{#if node.owner_display}
					<div class="flex items-center gap-1">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
						</svg>
						<span>Owner: <span class="font-medium text-surface-700 dark:text-surface-300">{node.owner_display}</span></span>
					</div>
				{/if}

				{#if node.risk_score}
					<div class="flex items-center gap-1">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
						<span>Risk Score: <span class="font-medium text-surface-700 dark:text-surface-300">{node.risk_score}</span></span>
					</div>
				{/if}

				{#if node.last_audited}
					<div class="flex items-center gap-1">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<span>Last Audited: <span class="font-medium text-surface-700 dark:text-surface-300">{formatDate(node.last_audited)}</span></span>
					</div>
				{/if}

				<div class="flex items-center gap-1">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<span>Updated: <span class="font-medium text-surface-700 dark:text-surface-300">{formatDateTime(node.updated_at)}</span></span>
				</div>
			</div>
		</div>
	</div>
	
	<!-- Children (Nested Entities) -->
	{#if node.children && node.children.length > 0 && isExpanded}
		<div class="mt-3 space-y-3 pl-8 border-l-2 border-surface-200 dark:border-surface-700">
			{#each node.children as childNode}
				<Self node={childNode} level={level + 1} />
			{/each}
		</div>
	{/if}
</div>

<style>
	.entity-card {
		position: relative;
	}

	.entity-card:hover {
		transform: translateY(-1px);
	}
</style>
