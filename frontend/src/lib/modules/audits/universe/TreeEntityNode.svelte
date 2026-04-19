<script lang="ts">
	import type { TreeViewNode } from '$lib/components/TreeView/types';
	import AuditEntityRow from './AuditEntityRow.svelte';
	import Self from './TreeEntityNode.svelte';

	interface Props {
		node: TreeViewNode;
		level?: number;
	}

	let { node, level = 0 }: Props = $props();

	// Type assertion for contentProps
	const contentProps = node.contentProps as any;
</script>

<div class="hover:bg-gray-50 rounded-md">
	<!-- Entity Row -->
	<div class="py-3 px-4" class:ml-6={level > 0} class:ml-12={level > 1} class:ml-18={level > 2} class:ml-24={level > 3}>
		<AuditEntityRow
			entity={contentProps.entity}
			formatEntityType={contentProps.formatEntityType}
			formatDate={contentProps.formatDate}
			formatDateTime={contentProps.formatDateTime}
			onDeleted={contentProps.onDeleted}
		/>
	</div>

	<!-- Children -->
	{#if node.children && node.children.length > 0}
		<div class="space-y-1">
			{#each node.children as childNode}
				<Self node={childNode} level={level + 1} />
			{/each}
		</div>
	{/if}
</div>
