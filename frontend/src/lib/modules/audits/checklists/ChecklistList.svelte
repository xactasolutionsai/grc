<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { listChecklists, deleteChecklist, duplicateChecklist } from './api.js';

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
		item_count: number;
	}

	let checklists = $state<Checklist[]>([]);
	let loading = $state(true);
	let error = $state('');
	let searchQuery = $state('');
	let filterStatus = $state('');
	let showDeleteModal = $state(false);
	let checklistToDelete: Checklist | null = $state(null);
	let deleteConfirmId: number | null = $state(null);
	let deleting = $state(false);

	// Status choices
	const statusChoices = [
		{ value: '', label: 'All Status' },
		{ value: 'draft', label: '📝 Draft' },
		{ value: 'active', label: '✅ Active' },
		{ value: 'archived', label: '📦 Archived' }
	];

	// Summary stats
	let summary = $state({
		total: 0,
		draft: 0,
		active: 0,
		archived: 0
	});

	onMount(async () => {
		await loadChecklists();
	});

	// Watch for search/filter changes
	$effect(() => {
		if (searchQuery !== undefined || filterStatus !== undefined) {
			loadChecklists();
		}
	});

	async function loadChecklists() {
		try {
			loading = true;
			error = '';

			const params: Record<string, string> = {};
			if (searchQuery) params.search = searchQuery;
			if (filterStatus) params.status = filterStatus;

			const data = await listChecklists(params);
			checklists = data.results || data;

			// Calculate summary
			summary.total = checklists.length;
			summary.draft = checklists.filter(c => c.status === 'draft').length;
			summary.active = checklists.filter(c => c.status === 'active').length;
			summary.archived = checklists.filter(c => c.status === 'archived').length;
		} catch (err) {
			console.error('Error loading checklists:', err);
			error = 'Failed to load checklists. Please try again.';
		} finally {
			loading = false;
		}
	}

	function clearFilters() {
		searchQuery = '';
		filterStatus = '';
	}

	function viewChecklist(id: number) {
		goto(`/audits/checklists/${id}`);
	}

	function createNewChecklist() {
		goto('/audits/checklists/new');
	}

	async function handleDuplicate(checklist: Checklist) {
		try {
			const duplicated = await duplicateChecklist(checklist.id);
			await loadChecklists();
			// Optionally navigate to the new checklist
			// goto(`/audits/checklists/${duplicated.id}`);
		} catch (err) {
			console.error('Error duplicating checklist:', err);
			error = 'Failed to duplicate checklist';
		}
	}

	function confirmDelete(checklist: Checklist) {
		checklistToDelete = checklist;
		deleteConfirmId = checklist.id;
	}

	async function handleDelete() {
		if (!deleteConfirmId) return;

		try {
			deleting = true;
			await deleteChecklist(deleteConfirmId);
			deleteConfirmId = null;
			checklistToDelete = null;
			await loadChecklists();
		} catch (err) {
			console.error('Error deleting checklist:', err);
			error = 'Failed to delete checklist';
		} finally {
			deleting = false;
		}
	}

	function cancelDelete() {
		deleteConfirmId = null;
		checklistToDelete = null;
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
	<!-- Header Card -->
	<div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 shadow-xl rounded-xl mb-8 p-8">
		<div class="flex justify-between items-center">
			<div class="flex items-center gap-4">
				<div class="p-3 bg-white/10 rounded-xl">
					<svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
					</svg>
				</div>
				<div>
					<h1 class="text-3xl font-bold text-white">Audit Checklists</h1>
					<p class="text-primary-100 mt-1">Manage reusable audit programs and test procedures</p>
				</div>
			</div>
			<button
				onclick={createNewChecklist}
				class="inline-flex items-center gap-2 px-6 py-3 border-2 border-white/30 text-sm font-semibold rounded-xl shadow-lg text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				Create Checklist
			</button>
		</div>
	</div>

	<!-- Summary Dashboard -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Total</p>
					<p class="text-3xl font-bold text-surface-900 dark:text-surface-50 mt-1">
						{summary.total}
					</p>
				</div>
				<div class="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
					<svg class="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
					</svg>
				</div>
			</div>
		</div>

		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Draft</p>
					<p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">
						{summary.draft}
					</p>
				</div>
				<div class="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
					<svg class="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
					</svg>
				</div>
			</div>
		</div>

		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Active</p>
					<p class="text-3xl font-bold text-success-600 dark:text-success-400 mt-1">
						{summary.active}
					</p>
				</div>
				<div class="p-3 bg-success-100 dark:bg-success-900/30 rounded-lg">
					<svg class="w-6 h-6 text-success-600 dark:text-success-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
			</div>
		</div>

		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Archived</p>
					<p class="text-3xl font-bold text-gray-600 dark:text-gray-400 mt-1">
						{summary.archived}
					</p>
				</div>
				<div class="p-3 bg-gray-100 dark:bg-gray-900/30 rounded-lg">
					<svg class="w-6 h-6 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
					</svg>
				</div>
			</div>
		</div>
	</div>

	<!-- Filters and Search -->
	<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6 mb-6">
		<div class="flex items-center justify-between mb-4">
			<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50">Filters</h2>
			<button
				onclick={clearFilters}
				class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-surface-700 dark:text-surface-300 bg-surface-100 dark:bg-surface-700 hover:bg-surface-200 dark:hover:bg-surface-600 rounded-lg transition-colors"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
				Clear Filters
			</button>
		</div>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<!-- Search -->
			<div>
				<label for="search-input" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
					🔍 Search
				</label>
				<input
					id="search-input"
					type="text"
					bind:value={searchQuery}
					placeholder="Search checklists..."
					class="w-full px-4 py-2.5 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
				/>
			</div>

			<!-- Status Filter -->
			<div>
				<label for="status-filter" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
					📊 Status
				</label>
				<select
					id="status-filter"
					bind:value={filterStatus}
					class="w-full px-4 py-2.5 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
				>
					{#each statusChoices as choice}
						<option value={choice.value}>{choice.label}</option>
					{/each}
				</select>
			</div>
		</div>
	</div>

	{#if loading}
		<div class="flex justify-center items-center py-16">
			<div class="flex flex-col items-center gap-4">
				<svg class="animate-spin h-12 w-12 text-primary-600" fill="none" viewBox="0 0 24 24">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
				</svg>
				<span class="text-surface-600 dark:text-surface-400 font-medium">Loading checklists...</span>
			</div>
		</div>
	{:else if error}
		<div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-4 mb-6 shadow-sm flex items-start gap-3">
			<svg class="h-5 w-5 text-error-600 dark:text-error-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<div class="text-error-800 dark:text-error-200">Error: {error}</div>
		</div>
	{:else}
		<div class="bg-white dark:bg-surface-800 shadow-xl rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-surface-200 dark:divide-surface-700">
					<thead>
						<tr class="bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900">
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
								📋 Name
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
								📊 Status
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
								📁 Folder
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
								🔢 Items
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
								👤 Created By
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
								📅 Created
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
								⚙️ Actions
							</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-surface-200 dark:divide-surface-700">
						{#each checklists as checklist}
							<tr class="hover:bg-surface-50 dark:hover:bg-surface-700/50 transition-colors">
								<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
									<button
										type="button"
										class="font-semibold truncate cursor-pointer text-left w-full hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
										onclick={() => viewChecklist(checklist.id)}
										title="{checklist.name}"
									>
										{checklist.name}
									</button>
									{#if checklist.description}
										<div class="text-xs text-surface-600 dark:text-surface-400 truncate max-w-md" title="{checklist.description}">{checklist.description}</div>
									{/if}
								</td>
								<td class="px-6 py-4">
									<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap {getStatusColor(checklist.status)}">
										{formatStatus(checklist.status)}
									</span>
								</td>
								<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
									<div class="truncate" title="{checklist.folder_name || '—'}">{checklist.folder_name || '—'}</div>
								</td>
								<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
									<span class="inline-flex items-center justify-center px-2.5 py-1 rounded-lg bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-300 text-xs font-bold">
										{checklist.item_count}
									</span>
								</td>
								<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
									<div class="truncate" title="{checklist.created_by_display || '—'}">{checklist.created_by_display || '—'}</div>
								</td>
								<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
									{formatDate(checklist.created_at)}
								</td>
								<td class="px-6 py-4">
									<div class="flex items-center gap-2">
										<button
											onclick={() => viewChecklist(checklist.id)}
											class="p-2 text-surface-600 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-700 rounded-lg transition-colors"
											title="View details"
											aria-label="View details"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
											</svg>
										</button>
										<button
											onclick={() => handleDuplicate(checklist)}
											class="p-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
											title="Duplicate"
											aria-label="Duplicate"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
											</svg>
										</button>
										<button
											onclick={() => confirmDelete(checklist)}
											class="p-2 text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/20 rounded-lg transition-colors"
											title="Delete checklist"
											aria-label="Delete checklist"
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

			{#if checklists.length === 0}
				<div class="text-center py-12 px-4">
					<svg class="mx-auto h-16 w-16 text-surface-400 dark:text-surface-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
					</svg>
					<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-2">No checklists found</h3>
					<p class="text-surface-600 dark:text-surface-400">Create your first checklist to get started.</p>
				</div>
			{/if}
		</div>
	{/if}

	<!-- Delete Confirmation Modal -->
	{#if deleteConfirmId}
		<div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
			<div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-surface-800">
				<div class="mt-3 text-center">
					<div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/30">
						<svg class="h-6 w-6 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
						</svg>
					</div>
					<h3 class="text-lg font-medium text-gray-900 dark:text-surface-50 mt-4">Delete Checklist</h3>
					<div class="mt-2 px-7 py-3">
						<p class="text-sm text-gray-500 dark:text-surface-400">
							Are you sure you want to delete checklist "<strong>{checklistToDelete?.name}</strong>"? This action cannot be undone.
						</p>
					</div>
					<div class="items-center px-4 py-3">
						<button
							onclick={handleDelete}
							disabled={deleting}
							class="px-4 py-2 bg-red-600 text-white text-base font-medium rounded-md w-24 mr-2 shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-300 disabled:opacity-50"
						>
							{deleting ? 'Deleting...' : 'Delete'}
						</button>
						<button
							onclick={cancelDelete}
							disabled={deleting}
							class="px-4 py-2 bg-gray-300 dark:bg-surface-600 text-gray-800 dark:text-surface-200 text-base font-medium rounded-md w-24 shadow-sm hover:bg-gray-400 dark:hover:bg-surface-500 focus:outline-none focus:ring-2 focus:ring-gray-300 disabled:opacity-50"
						>
							Cancel
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>
