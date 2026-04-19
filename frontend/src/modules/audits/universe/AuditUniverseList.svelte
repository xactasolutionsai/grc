<script>
	import { onMount } from 'svelte';
	import { listEntities } from './api.js';

	let entities = [];
	let loading = true;
	let error = null;

	onMount(async () => {
		try {
			const data = await listEntities();
			entities = data.results || data;
			loading = false;
		} catch (err) {
			console.error('Error loading entities:', err);
			error = err.message;
			loading = false;
		}
	});

	function formatEntityType(type) {
		return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
	}

	function formatDate(dateString) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleDateString();
	}
</script>

<div class="p-6">
	<h1 class="text-3xl font-bold text-gray-900 mb-6">Audit Universe</h1>

	{#if loading}
		<div class="flex justify-center items-center py-8">
			<div class="text-gray-600">Loading audit universe…</div>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 rounded-md p-4">
			<div class="text-red-800">Error: {error}</div>
		</div>
	{:else}
		<div class="bg-white shadow overflow-hidden sm:rounded-md">
			<table class="min-w-full divide-y divide-gray-200">
				<thead class="bg-gray-50">
					<tr>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Name
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Type
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Owner
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Risk Score
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Last Audited
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Status
						</th>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each entities as entity}
						<tr class="hover:bg-gray-50">
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm font-medium text-gray-900">{entity.name}</div>
								{#if entity.description}
									<div class="text-sm text-gray-500">{entity.description}</div>
								{/if}
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
									{formatEntityType(entity.entity_type)}
								</span>
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
								{entity.owner ? entity.owner.username : '—'}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
								{entity.risk_score}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
								{formatDate(entity.last_audited)}
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {entity.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
									{entity.is_active ? 'Active' : 'Inactive'}
								</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>

			{#if entities.length === 0}
				<div class="text-center py-8 text-gray-500">
					No audit entities found. Create your first entity to get started.
				</div>
			{/if}
		</div>
	{/if}
</div>
