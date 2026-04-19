<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getChecklist, deleteChecklistItem, createChecklistItem, updateChecklistItem } from './api.js';
	import EnhancedModal from '$lib/components/Modals/EnhancedModal.svelte';

	interface Props {
		checklistId: string;
	}

	let { checklistId }: Props = $props();

	interface ChecklistItem {
		id: number;
		title: string;
		description: string;
		order: number;
		control: number | null;
		control_name: string | null;
		control_display: any;
		risk: number | null;
		risk_name: string | null;
		risk_display: any;
		policy: number | null;
		policy_name: string | null;
		policy_display: any;
	}

	interface Checklist {
		id: number;
		name: string;
		description: string;
		folder: number | null;
		folder_name: string | null;
		status: string;
		is_published: boolean;
		created_by: number | null;
		created_by_display: string | null;
		created_at: string;
		updated_at: string;
		items: ChecklistItem[];
		item_count: number;
	}

	let checklist = $state<Checklist | null>(null);
	let loading = $state(true);
	let error = $state('');
	let showAddItemModal = $state(false);
	let editingItem: ChecklistItem | null = $state(null);
	let newItem = $state({
		title: '',
		description: '',
		order: 0,
		control: null as number | null,
		risk: null as number | null,
		policy: null as number | null
	});

	// Available controls, risks, policies - would load from API
	let availableControls = $state<Array<{id: number, name: string}>>([]);
	let availableRisks = $state<Array<{id: number, name: string}>>([]);
	let availablePolicies = $state<Array<{id: number, name: string}>>([]);

	onMount(async () => {
		await Promise.all([loadChecklist(), loadReferenceData()]);
	});

	async function loadChecklist() {
		try {
			loading = true;
			error = '';
			checklist = await getChecklist(checklistId);
		} catch (err) {
			console.error('Error loading checklist:', err);
			error = 'Failed to load checklist. Please try again.';
		} finally {
			loading = false;
		}
	}

	async function loadReferenceData() {
		try {
			// Load available controls
			const controlsResponse = await fetch('/fe-api/applied-controls/');
			if (controlsResponse.ok) {
				const controlsData = await controlsResponse.json();
				availableControls = (controlsData.results || controlsData).slice(0, 100).map((c: any) => ({
					id: c.id,
					name: c.name || `Control ${c.id}`
				}));
			}

			// Load available risks
			const risksResponse = await fetch('/fe-api/risk-scenarios/');
			if (risksResponse.ok) {
				const risksData = await risksResponse.json();
				availableRisks = (risksData.results || risksData).slice(0, 100).map((r: any) => ({
					id: r.id,
					name: r.name || `Risk ${r.id}`
				}));
			}

		// Load available policies
		const policiesResponse = await fetch('/fe-api/policies/');
		if (policiesResponse.ok) {
			const policiesData = await policiesResponse.json();
			availablePolicies = (policiesData.results || policiesData).slice(0, 100).map((p: any) => ({
				id: p.id,
				name: p.name || `Policy ${p.id}`
			}));
		}
		} catch (err) {
			console.error('Error loading reference data:', err);
		}
	}

	function goBack() {
		goto('/audits/checklists');
	}

	function editChecklist() {
		goto(`/audits/checklists/${checklistId}/edit`);
	}

	function openAddItemModal() {
		newItem = {
			title: '',
			description: '',
			order: checklist?.items.length || 0,
			control: null,
			risk: null,
			policy: null
		};
		editingItem = null;
		showAddItemModal = true;
	}

	function openEditItemModal(item: ChecklistItem) {
		newItem = {
			title: item.title,
			description: item.description,
			order: item.order,
			control: item.control,
			risk: item.risk,
			policy: item.policy
		};
		editingItem = item;
		showAddItemModal = true;
	}

	async function handleSaveItem() {
		if (!newItem.title.trim()) {
			error = 'Title is required';
			return;
		}

		try {
			const itemData = {
				checklist: checklistId,
				title: newItem.title,
				description: newItem.description,
				order: newItem.order,
				control: newItem.control || null,
				risk: newItem.risk || null,
				policy: newItem.policy || null
			};

			if (editingItem) {
				await updateChecklistItem(editingItem.id, itemData);
			} else {
				await createChecklistItem(itemData);
			}

			showAddItemModal = false;
			await loadChecklist();
			error = '';
		} catch (err) {
			console.error('Error saving item:', err);
			error = 'Failed to save item';
		}
	}

	function cancelItemModal() {
		showAddItemModal = false;
		editingItem = null;
	}

	async function handleDeleteItem(item: ChecklistItem) {
		if (!confirm(`Are you sure you want to delete "${item.title}"?`)) {
			return;
		}

		try {
			await deleteChecklistItem(item.id);
			await loadChecklist();
		} catch (err) {
			console.error('Error deleting item:', err);
			error = 'Failed to delete item';
		}
	}

	function getStatusColor(status: string): string {
		switch (status) {
			case 'draft':
				return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
			case 'active':
				return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
			case 'archived':
				return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
			default:
				return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
		}
	}

	function formatDate(dateString: string): string {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleDateString();
	}

	function formatStatus(status: string): string {
		const statusMap: Record<string, string> = {
			draft: '📝 Draft',
			active: '✅ Active',
			archived: '📦 Archived'
		};
		return statusMap[status] || status;
	}
</script>

<div class="p-6">
	{#if loading}
		<div class="flex justify-center items-center py-16">
			<div class="flex flex-col items-center gap-4">
				<svg class="animate-spin h-12 w-12 text-primary-600" fill="none" viewBox="0 0 24 24">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
				</svg>
				<span class="text-surface-600 dark:text-surface-400 font-medium">Loading checklist...</span>
			</div>
		</div>
	{:else if error && !checklist}
		<div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-4 mb-6 shadow-sm flex items-start gap-3">
			<svg class="h-5 w-5 text-error-600 dark:text-error-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<div class="text-error-800 dark:text-error-200">Error: {error}</div>
		</div>
	{:else if checklist}
		<!-- Header Card -->
		<div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 shadow-xl rounded-xl mb-8 p-8">
			<div class="flex items-center gap-4 mb-4">
				<button
					onclick={goBack}
					class="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-white"
					title="Back to list"
					aria-label="Back to list"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
					</svg>
				</button>
				<div class="flex-1">
					<h1 class="text-3xl font-bold text-white">{checklist.name}</h1>
					{#if checklist.description}
						<p class="text-primary-100 mt-2">{checklist.description}</p>
					{/if}
				</div>
				<span class="inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold {getStatusColor(checklist.status)} shadow-md">
					{formatStatus(checklist.status)}
				</span>
				<button
					onclick={editChecklist}
					class="inline-flex items-center gap-2 px-6 py-3 border-2 border-white/30 text-sm font-semibold rounded-xl shadow-lg text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
					</svg>
					Edit Checklist
				</button>
			</div>
		</div>

		<!-- Info Cards -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
			<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
				<div class="flex items-center gap-3">
					<div class="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
						<svg class="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
						</svg>
					</div>
					<div>
						<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Folder</p>
						<p class="text-lg font-bold text-surface-900 dark:text-surface-50">{checklist.folder_name || 'None'}</p>
					</div>
				</div>
			</div>

			<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
				<div class="flex items-center gap-3">
					<div class="p-3 bg-success-100 dark:bg-success-900/30 rounded-lg">
						<svg class="w-6 h-6 text-success-600 dark:text-success-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
						</svg>
					</div>
					<div>
						<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Total Items</p>
						<p class="text-lg font-bold text-surface-900 dark:text-surface-50">{checklist.item_count}</p>
					</div>
				</div>
			</div>

			<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
				<div class="flex items-center gap-3">
					<div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
						<svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
						</svg>
					</div>
					<div>
						<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Created By</p>
						<p class="text-lg font-bold text-surface-900 dark:text-surface-50">{checklist.created_by_display || 'Unknown'}</p>
					</div>
				</div>
			</div>

			<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
				<div class="flex items-center gap-3">
					<div class="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
						<svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
						</svg>
					</div>
					<div>
						<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Created</p>
						<p class="text-lg font-bold text-surface-900 dark:text-surface-50">{formatDate(checklist.created_at)}</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Items Section -->
		<div class="bg-white dark:bg-surface-800 shadow-xl rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
			<div class="p-6 border-b border-surface-200 dark:border-surface-700 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900">
				<div class="flex justify-between items-center">
					<h2 class="text-xl font-bold text-surface-900 dark:text-surface-50">
						Checklist Items ({checklist.item_count})
					</h2>
					<button
						onclick={openAddItemModal}
						class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg shadow-md transition-colors font-semibold"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
						Add Item
					</button>
				</div>
			</div>

			{#if error}
				<div class="m-6 bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-4 shadow-sm flex items-start gap-3">
					<svg class="h-5 w-5 text-error-600 dark:text-error-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<div class="text-error-800 dark:text-error-200">{error}</div>
				</div>
			{/if}

			{#if checklist.items.length === 0}
				<div class="text-center py-12 px-4">
					<svg class="mx-auto h-16 w-16 text-surface-400 dark:text-surface-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
					</svg>
					<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-2">No items yet</h3>
					<p class="text-surface-600 dark:text-surface-400 mb-4">Add your first checklist item to get started.</p>
					<button
						onclick={openAddItemModal}
						class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg shadow-md transition-colors font-semibold"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
						Add First Item
					</button>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-surface-200 dark:divide-surface-700">
						<thead>
							<tr class="bg-surface-50 dark:bg-surface-900">
								<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap w-16">
									#
								</th>
								<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
									📋 Title
								</th>
								<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
									📝 Description
								</th>
								<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
									🎯 Control
								</th>
								<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
									⚠️ Risk
								</th>
								<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
									📄 Policy
								</th>
								<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
									⚙️ Actions
								</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-surface-200 dark:divide-surface-700">
							{#each checklist.items as item}
								<tr class="hover:bg-surface-50 dark:hover:bg-surface-700/50 transition-colors">
									<td class="px-6 py-4 text-sm font-mono text-surface-600 dark:text-surface-400">
										{item.order}
									</td>
									<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
										<div class="font-semibold">{item.title}</div>
									</td>
									<td class="px-6 py-4 text-sm text-surface-600 dark:text-surface-400">
										<div class="truncate max-w-md" title="{item.description || '—'}">
											{item.description || '—'}
										</div>
									</td>
									<td class="px-6 py-4 text-sm">
										{#if item.control_name}
											<span class="inline-flex items-center px-2.5 py-1 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-xs font-medium" title={item.control_name}>
												{item.control_name}
											</span>
										{:else}
											<span class="text-surface-400">—</span>
										{/if}
									</td>
									<td class="px-6 py-4 text-sm">
										{#if item.risk_name}
											<span class="inline-flex items-center px-2.5 py-1 rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 text-xs font-medium" title={item.risk_name}>
												{item.risk_name}
											</span>
										{:else}
											<span class="text-surface-400">—</span>
										{/if}
									</td>
									<td class="px-6 py-4 text-sm">
										{#if item.policy_name}
											<span class="inline-flex items-center px-2.5 py-1 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 text-xs font-medium" title={item.policy_name}>
												{item.policy_name}
											</span>
										{:else}
											<span class="text-surface-400">—</span>
										{/if}
									</td>
									<td class="px-6 py-4">
										<div class="flex items-center gap-2">
											<button
												onclick={() => openEditItemModal(item)}
												class="p-2 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
												title="Edit item"
												aria-label="Edit item"
											>
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
												</svg>
											</button>
											<button
												onclick={() => handleDeleteItem(item)}
												class="p-2 text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/20 rounded-lg transition-colors"
												title="Delete item"
												aria-label="Delete item"
											>
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
												</svg>
											</button>
										</div>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>
	{/if}
</div>

<!-- Add/Edit Item Modal -->
<EnhancedModal
	bind:open={showAddItemModal}
	title="{editingItem ? '✏️ Edit' : '➕ Add'} Checklist Item"
	maxWidth="3xl"
	showFooter={false}
	onClose={cancelItemModal}
>
	<div class="space-y-6">
		<!-- Title -->
		<div>
			<label for="item-title" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
				Title <span class="text-error-500">*</span>
			</label>
			<input
				id="item-title"
				type="text"
				bind:value={newItem.title}
				placeholder="Enter item title"
				class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
			/>
		</div>

		<!-- Description -->
		<div>
			<label for="item-description" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
				Description
			</label>
			<textarea
				id="item-description"
				bind:value={newItem.description}
				placeholder="Enter item description or test objective"
				rows="3"
				class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
			></textarea>
		</div>

		<!-- Order -->
		<div>
			<label for="item-order" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
				Order
			</label>
			<input
				id="item-order"
				type="number"
				bind:value={newItem.order}
				min="0"
				class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
			/>
		</div>

		<!-- Links -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			<!-- Control -->
			<div>
				<label for="item-control" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
					🎯 Control
				</label>
				<select
					id="item-control"
					bind:value={newItem.control}
					class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
				>
					<option value={null}>None</option>
					{#each availableControls as control}
						<option value={control.id}>{control.name}</option>
					{/each}
				</select>
			</div>

			<!-- Risk -->
			<div>
				<label for="item-risk" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
					⚠️ Risk
				</label>
				<select
					id="item-risk"
					bind:value={newItem.risk}
					class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
				>
					<option value={null}>None</option>
					{#each availableRisks as risk}
						<option value={risk.id}>{risk.name}</option>
					{/each}
				</select>
			</div>

			<!-- Policy -->
			<div>
				<label for="item-policy" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
					📄 Policy
				</label>
				<select
					id="item-policy"
					bind:value={newItem.policy}
					class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
				>
					<option value={null}>None</option>
					{#each availablePolicies as policy}
						<option value={policy.id}>{policy.name}</option>
					{/each}
				</select>
			</div>
		</div>

		<!-- Footer Buttons -->
		<div class="flex justify-end gap-3 mt-8 pt-6 border-t border-surface-200 dark:border-surface-700">
			<button
				onclick={cancelItemModal}
				class="px-6 py-3 border-2 border-surface-300 dark:border-surface-600 rounded-xl shadow-sm text-sm font-semibold text-surface-700 dark:text-surface-200 bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 transition-all flex items-center gap-2"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
				Cancel
			</button>
			<button
				onclick={handleSaveItem}
				class="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl shadow-lg text-sm font-semibold transition-all flex items-center gap-2"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
				</svg>
				{editingItem ? 'Update' : 'Save'} Item
			</button>
		</div>
	</div>
</EnhancedModal>
