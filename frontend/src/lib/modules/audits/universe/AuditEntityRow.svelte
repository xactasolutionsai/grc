<script lang="ts">
	import { deleteEntity } from './api.js';

	interface Props {
		entity: any;
		formatEntityType: (type: string) => string;
		formatDate: (dateString: string | null) => string;
		formatDateTime: (dateString: string | null) => string;
		onDeleted: (event: CustomEvent) => void;
	}

	let { entity, formatEntityType, formatDate, formatDateTime, onDeleted }: Props = $props();
	
	let showDeleteConfirm = false;
	let deleting = $state(false);

	async function handleDelete() {
		if (!confirm(`Are you sure you want to delete "${entity.name}"? This action cannot be undone.`)) {
			return;
		}

		try {
			deleting = true;
			await deleteEntity(entity.id);
			onDeleted(new CustomEvent('deleted', { detail: { id: entity.id } }));
		} catch (error) {
			console.error('Error deleting entity:', error);
			alert('Failed to delete entity. Please try again.');
		} finally {
			deleting = false;
		}
	}
</script>

<div class="grid grid-cols-16 gap-2 items-center">
	<!-- Name Column -->
	<div class="col-span-3">
		<div class="text-sm font-medium text-gray-900 truncate">
			{entity.name}
		</div>
		{#if entity.description}
			<div class="text-xs text-gray-500 truncate">
				{entity.description}
			</div>
		{/if}
		{#if entity.parent_name}
			<div class="text-xs text-blue-600 truncate">
				Parent: {entity.parent_name}
			</div>
		{/if}
	</div>
	
	<!-- Type Column -->
	<div class="col-span-2">
		<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
			{formatEntityType(entity.entity_type)}
		</span>
	</div>
	
	<!-- Owner Column -->
	<div class="col-span-2 text-sm text-gray-900 truncate">
		{entity.owner_username || '—'}
	</div>
	
	<!-- Risk Score Column -->
	<div class="col-span-1 text-sm text-gray-900 text-center">
		{entity.risk_score}
	</div>
	
	<!-- Last Audited Column -->
	<div class="col-span-2 text-sm text-gray-900">
		{formatDate(entity.last_audited)}
	</div>
	
	<!-- Status Column -->
	<div class="col-span-1 text-center">
		<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium {entity.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
			{entity.is_active ? 'Active' : 'Inactive'}
		</span>
	</div>
	
	<!-- Created At Column -->
	<div class="col-span-2 text-sm text-gray-500">
		{formatDateTime(entity.created_at)}
	</div>
	
	<!-- Updated At Column -->
	<div class="col-span-2 text-sm text-gray-500">
		{formatDateTime(entity.updated_at)}
	</div>
	
	<!-- Actions Column -->
	<div class="col-span-1 flex justify-center">
		<button
			onclick={handleDelete}
			disabled={deleting}
			class="text-red-600 hover:text-red-800 disabled:opacity-50 disabled:cursor-not-allowed p-1"
			title="Delete entity"
		>
			{#if deleting}
				<svg class="h-4 w-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
				</svg>
			{:else}
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
				</svg>
			{/if}
		</button>
	</div>
</div>
