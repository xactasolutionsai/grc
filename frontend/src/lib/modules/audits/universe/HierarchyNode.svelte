<script lang="ts">
	export let rootNode: any;
	export let currentEntityId: number;
	export let level = 0;

	let expanded = level < 2; // Auto-expand first 2 levels

	function toggleExpanded() {
		expanded = !expanded;
	}

	function formatEntityType(type: string) {
		return type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
	}

	function getEntityTypeColor(type: string) {
		const colors: Record<string, string> = {
			'business_unit': 'bg-blue-100 text-blue-800',
			'division': 'bg-green-100 text-green-800',
			'function': 'bg-purple-100 text-purple-800',
			'section': 'bg-yellow-100 text-yellow-800',
			'unit': 'bg-orange-100 text-orange-800',
			'process': 'bg-red-100 text-red-800',
			'system': 'bg-indigo-100 text-indigo-800',
			'vendor': 'bg-pink-100 text-pink-800',
			'compliance_domain': 'bg-gray-100 text-gray-800'
		};
		return colors[type] || 'bg-gray-100 text-gray-800';
	}

	function getRiskScoreColor(score: number) {
		if (score >= 8) return 'text-red-600';
		if (score >= 6) return 'text-orange-600';
		if (score >= 4) return 'text-yellow-600';
		return 'text-green-600';
	}
</script>

<div class="border-l-2 border-surface-200 pl-3 {level > 0 ? 'ml-4' : ''}">
	<div class="flex items-center space-x-2 py-1">
		{#if rootNode.children && rootNode.children.length > 0}
			<button
				onclick={toggleExpanded}
				class="flex items-center justify-center w-4 h-4 text-surface-400 hover:text-surface-600"
				aria-label={expanded ? 'Collapse' : 'Expand'}
			>
				<svg class="w-3 h-3 transition-transform {expanded ? 'rotate-90' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
				</svg>
			</button>
		{:else}
			<div class="w-4 h-4"></div>
		{/if}
		
		<a
			href="/audits/universe/{rootNode.id}"
			class="flex-1 flex items-center space-x-2 py-1 px-2 rounded hover:bg-surface-100 {rootNode.id === currentEntityId ? 'bg-primary-50 border border-primary-200' : ''}"
		>
			<span class="text-sm font-medium {rootNode.id === currentEntityId ? 'text-primary-700' : 'text-surface-900'}">
				{rootNode.name}
			</span>
			<span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium {getEntityTypeColor(rootNode.entity_type)}">
				{formatEntityType(rootNode.entity_type)}
			</span>
			{#if rootNode.risk_score}
				<span class="text-xs {getRiskScoreColor(rootNode.risk_score)}">
					Risk: {rootNode.risk_score}
				</span>
			{/if}
			{#if rootNode.active === false}
				<span class="text-xs text-surface-400">(Inactive)</span>
			{/if}
		</a>
	</div>
	
	{#if rootNode.children && rootNode.children.length > 0 && expanded}
		<div class="space-y-1">
			{#each rootNode.children as child}
				<svelte:self rootNode={child} {currentEntityId} level={level + 1} />
			{/each}
		</div>
	{/if}
</div>
