<script lang="ts">
	import { onMount } from 'svelte';
	import { getHierarchy } from './api.js';
	import HierarchyTreeNode from './HierarchyTreeNode.svelte';

	export let refreshTrigger = 0;
	export let filterTab: string = 'all'; // Filter tab: 'all', 'my_entities', 'my_team'

	let hierarchy: any[] = [];
	let loading = true;
	let error: string | null = null;
	let expandedNodes: Set<number> = new Set();
	let mounted = false;
	let lastFilterTab = '';

	onMount(() => {
		mounted = true;
	});

	// Watch for refresh trigger changes - load hierarchy
	$: if (refreshTrigger && mounted) {
		loadHierarchy();
	}

	// Watch for filter tab changes - load hierarchy when filterTab changes
	$: if (mounted && filterTab !== lastFilterTab) {
		lastFilterTab = filterTab;
		loadHierarchy();
	}

	async function loadHierarchy() {
		try {
			loading = true;
			error = null;

			// Build params based on filter tab
			const params: any = {};
			if (filterTab === 'my_entities') {
				params.my_entities = 'true';
			} else if (filterTab === 'my_team') {
				params.my_team = 'true';
			}

			hierarchy = await getHierarchy(params);
		} catch (err: any) {
			console.error('Error loading hierarchy:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	}

	function toggleNode(nodeId: number) {
		if (expandedNodes.has(nodeId)) {
			expandedNodes.delete(nodeId);
		} else {
			expandedNodes.add(nodeId);
		}
		expandedNodes = expandedNodes; // Trigger reactivity
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

{#if loading}
	<div class="flex justify-center items-center py-8">
		<div class="text-surface-600">Loading organizational structure…</div>
	</div>
{:else if error}
	<div class="bg-error-50 border border-error-200 rounded-md p-4">
		<div class="text-error-800">Error: {error}</div>
		<button
			onclick={loadHierarchy}
			class="mt-2 px-4 py-2 bg-error-600 text-white rounded-md hover:bg-error-700"
		>
			Retry
		</button>
	</div>
{:else if hierarchy.length === 0}
	<div class="text-center py-8 text-surface-500">
		No organizational structure found. Create entities with parent-child relationships to see the hierarchy.
	</div>
{:else}
	<div class="space-y-2">
		{#each hierarchy as node}
			<HierarchyTreeNode {node} {expandedNodes} {toggleNode} />
		{/each}
	</div>
{/if}
