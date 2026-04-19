<script lang="ts">
	export let node;
	export let expandedNodes;
	export let toggleNode;
	export let level = 0;

	$: hasChildren = node.children && node.children.length > 0;
	$: isExpanded = expandedNodes.has(node.id);
	$: indentClass = `ml-${level * 6}`;

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

<div class="border border-surface-200 rounded-lg bg-surface-50 hover:bg-surface-100 transition-colors">
	<div class="flex items-center justify-between p-4 {indentClass}">
		<div class="flex items-center space-x-3 flex-1">
			{#if hasChildren}
				<button
					onclick={() => toggleNode(node.id)}
					class="flex items-center justify-center w-6 h-6 rounded hover:bg-surface-200 transition-colors"
					aria-label={isExpanded ? 'Collapse' : 'Expand'}
				>
					{#if isExpanded}
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
						</svg>
					{:else}
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
						</svg>
					{/if}
				</button>
			{:else}
				<div class="w-6"></div>
			{/if}

			<div class="flex-1 min-w-0">
				<div class="flex items-center space-x-2">
					<a
						href="/audits/universe/{node.id}"
						class="text-lg font-medium text-surface-900 hover:text-primary-600 truncate"
					>
						{node.name}
					</a>
					<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium {getEntityTypeColor(node.entity_type)}">
						{formatEntityType(node.entity_type)}
					</span>
					{#if !node.is_active}
						<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
							Inactive
						</span>
					{/if}
				</div>
				{#if node.description}
					<p class="text-sm text-surface-600 mt-1 truncate">{node.description}</p>
				{/if}
			</div>
		</div>

		<div class="flex items-center space-x-4 text-sm">
			{#if node.risk_score !== null && node.risk_score !== undefined}
				<div class="flex items-center space-x-1">
					<span class="text-surface-500">Risk:</span>
					<span class="font-medium {getRiskScoreColor(node.risk_score)}">
						{node.risk_score.toFixed(1)}
					</span>
				</div>
			{/if}

			<div class="flex items-center space-x-2">
				<a
					href="/audits/universe/{node.id}"
					class="text-primary-600 hover:text-primary-800 p-1"
					title="View details"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
					</svg>
				</a>
			</div>
		</div>
	</div>

		{#if hasChildren && isExpanded}
			<div class="border-t border-surface-200 bg-surface-25">
				{#each node.children as child}
					<svelte:self node={child} {expandedNodes} {toggleNode} level={level + 1} />
				{/each}
			</div>
		{/if}
</div>
