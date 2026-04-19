<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { listWorkpapers, deleteWorkpaper } from './api.js';

	export let refreshTrigger = 0;

	let workpapers: any[] = [];
	let loading = true;
	let error: string | null = null;
	let searchQuery = '';
	let filterType = '';
	let filterStatus = '';
	let activeTab = 'all'; // 'all', 'my_uploads', 'pending_review', 'approved'
	let mounted = false;
	let searchTimeout: number | undefined;

	onMount(() => {
		mounted = true;
		loadWorkpapers();
	});

	onDestroy(() => {
		if (searchTimeout) clearTimeout(searchTimeout);
	});

	// Watch for refresh trigger changes
	$: if (refreshTrigger > 0) {
		loadWorkpapers();
	}

	// Debounced search - only trigger after user stops typing
	$: {
		searchQuery;

		if (mounted) {
			if (searchTimeout) clearTimeout(searchTimeout);
			searchTimeout = setTimeout(() => {
				loadWorkpapers();
			}, 300) as unknown as number;
		}
	}

	// Immediate filter changes (no debounce needed for dropdowns/tabs)
	$: {
		filterType;
		filterStatus;
		activeTab;

		if (mounted) {
			loadWorkpapers();
		}
	}

	async function loadWorkpapers() {
		try {
			loading = true;
			error = null;

			const params: Record<string, any> = {};
			if (searchQuery) params.search = searchQuery;
			if (filterType) params.workpaper_type = filterType;
			if (filterStatus) params.status = filterStatus;

			// Handle filter tabs
			if (activeTab === 'my_uploads') {
				params.my_uploads = 'true';
			} else if (activeTab === 'pending_review') {
				params.pending_review = 'true';
			} else if (activeTab === 'approved') {
				params.status = 'approved';
			}

			const data: any = await listWorkpapers(params);
			workpapers = data.results || data;
		} catch (err: any) {
			console.error('Error loading workpapers:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	}

	function handleTabChange(tab: string) {
		activeTab = tab;
	}

	function formatDate(dateString: string | null) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleDateString();
	}

	function formatFileSize(bytes: number | null) {
		if (!bytes) return '—';
		const units = ['B', 'KB', 'MB', 'GB'];
		let size = bytes;
		let unitIndex = 0;
		while (size >= 1024 && unitIndex < units.length - 1) {
			size /= 1024;
			unitIndex++;
		}
		return `${size.toFixed(1)} ${units[unitIndex]}`;
	}

	function getStatusColor(status: string) {
		switch (status) {
			case 'collected':
				return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200';
			case 'reviewed':
				return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200';
			case 'approved':
				return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200';
			default:
				return 'bg-surface-100 text-surface-800 dark:bg-surface-700 dark:text-surface-200';
		}
	}

	function getTypeIcon(type: string) {
		switch (type) {
			case 'excel':
				return '📊';
			case 'word':
				return '📄';
			case 'pdf':
				return '📋';
			case 'image':
				return '🖼️';
			case 'link':
				return '🔗';
			default:
				return '📎';
		}
	}

	async function handleDelete(id: number) {
		if (confirm('Are you sure you want to delete this workpaper?')) {
			try {
				await deleteWorkpaper(id);
				await loadWorkpapers();
			} catch (err: any) {
				console.error('Error deleting workpaper:', err);
				alert('Failed to delete workpaper: ' + err.message);
			}
		}
	}
</script>

{#if error}
	<div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-4 flex items-start gap-3">
		<svg class="h-5 w-5 text-error-600 dark:text-error-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
		</svg>
		<div class="text-error-800 dark:text-error-200">{error}</div>
	</div>
{:else}
	<!-- Filter Tabs -->
	<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-2 mb-6">
		<div class="flex gap-2">
			<button
				onclick={() => handleTabChange('all')}
				class="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all {activeTab === 'all' ? 'bg-primary-600 text-white shadow-md' : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700'}"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
				</svg>
				All Workpapers
			</button>
			<button
				onclick={() => handleTabChange('my_uploads')}
				class="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all {activeTab === 'my_uploads' ? 'bg-primary-600 text-white shadow-md' : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700'}"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
				</svg>
				My Uploads
			</button>
			<button
				onclick={() => handleTabChange('pending_review')}
				class="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all {activeTab === 'pending_review' ? 'bg-primary-600 text-white shadow-md' : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700'}"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				Pending Review
			</button>
			<button
				onclick={() => handleTabChange('approved')}
				class="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all {activeTab === 'approved' ? 'bg-primary-600 text-white shadow-md' : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700'}"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				Approved
			</button>
		</div>
	</div>

	<div class="bg-white dark:bg-surface-900 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
		<!-- Search and Filters -->
		<div class="bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 px-6 py-5 border-b border-surface-200 dark:border-surface-700">
			<div class="flex flex-col gap-4">
				<div class="flex flex-col sm:flex-row gap-3">
					<!-- Search Input -->
					<div class="flex-1 relative">
						<svg class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
						</svg>
						<input
							type="text"
							placeholder="Search workpapers..."
							bind:value={searchQuery}
							class="w-full pl-10 pr-4 py-2.5 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-50 placeholder-surface-400"
						/>
					</div>

					<!-- Type Filter -->
					<div class="sm:w-52">
						<select
							bind:value={filterType}
							class="w-full px-4 py-2.5 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-50"
						>
							<option value="">All Types</option>
							<option value="excel">📊 Excel</option>
							<option value="word">📄 Word</option>
							<option value="pdf">📋 PDF</option>
							<option value="image">🖼️ Image</option>
							<option value="link">🔗 Link</option>
							<option value="other">📎 Other</option>
						</select>
					</div>

					<!-- Status Filter -->
					<div class="sm:w-36">
						<select
							bind:value={filterStatus}
							class="w-full px-4 py-2.5 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-50"
						>
							<option value="">All Status</option>
							<option value="collected">📥 Collected</option>
							<option value="reviewed">👁️ Reviewed</option>
							<option value="approved">✅ Approved</option>
						</select>
					</div>

					<!-- Clear Filters Button -->
					<div class="sm:w-36">
						<button
							onclick={() => {
								searchQuery = '';
								filterType = '';
								filterStatus = '';
							}}
							class="w-full px-4 py-2.5 text-sm font-medium text-surface-700 dark:text-surface-300 bg-white dark:bg-surface-800 border border-surface-300 dark:border-surface-600 rounded-lg hover:bg-surface-50 dark:hover:bg-surface-700 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors flex items-center justify-center gap-2"
						>
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
							Clear
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- Workpapers List -->
		<div class="p-6 relative">
			<!-- Loading overlay (non-blocking) -->
			{#if loading}
				<div class="absolute top-2 right-2 z-10">
					<div class="flex items-center gap-2 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-700 rounded-lg px-3 py-1.5 shadow-sm">
						<svg class="animate-spin h-4 w-4 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						<span class="text-xs font-medium text-primary-700 dark:text-primary-300">Loading...</span>
					</div>
				</div>
			{/if}

			<div class="mb-4 text-sm text-surface-500 dark:text-surface-400">
				<span class="font-medium text-surface-900 dark:text-surface-50">{workpapers.length}</span> {workpapers.length === 1 ? 'workpaper' : 'workpapers'}
			</div>

			{#if workpapers.length > 0}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					{#each workpapers as workpaper}
						<div class="border border-surface-200 dark:border-surface-700 rounded-lg p-4 hover:shadow-lg transition-shadow bg-white dark:bg-surface-800">
							<!-- Header -->
							<div class="flex items-start justify-between mb-3">
								<div class="flex items-start gap-2">
									<span class="text-2xl">{getTypeIcon(workpaper.workpaper_type)}</span>
									<div>
										<h3 class="font-semibold text-surface-900 dark:text-surface-50">{workpaper.title}</h3>
										<span class="text-xs px-2 py-1 rounded-full {getStatusColor(workpaper.status)} inline-block mt-1">
											{workpaper.status}
										</span>
									</div>
								</div>
							</div>

							<!-- Description -->
							{#if workpaper.description}
								<p class="text-sm text-surface-600 dark:text-surface-300 mb-3 line-clamp-2">
									{workpaper.description}
								</p>
							{/if}

							<!-- Meta Info -->
							<div class="text-xs text-surface-500 dark:text-surface-400 space-y-1 mb-3">
								{#if workpaper.uploaded_by_display}
									<div class="flex items-center gap-1">
										<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
										</svg>
										<span>{workpaper.uploaded_by_display.name}</span>
									</div>
								{/if}
								<div class="flex items-center gap-1">
									<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
									</svg>
									<span>{formatDate(workpaper.created_at)}</span>
								</div>
								{#if workpaper.file_size}
									<div class="flex items-center gap-1">
										<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
										</svg>
										<span>{formatFileSize(workpaper.file_size)}</span>
									</div>
								{/if}
							</div>

							<!-- Tags -->
							{#if workpaper.tags && workpaper.tags.length > 0}
								<div class="flex flex-wrap gap-1 mb-3">
									{#each workpaper.tags.slice(0, 3) as tag}
										<span class="text-[10px] px-1.5 py-0.5 rounded bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-200">
											{tag}
										</span>
									{/each}
									{#if workpaper.tags.length > 3}
										<span class="text-[10px] px-1.5 py-0.5 rounded bg-surface-100 dark:bg-surface-700 text-surface-600 dark:text-surface-300">
											+{workpaper.tags.length - 3}
										</span>
									{/if}
								</div>
							{/if}

							<!-- Actions -->
							<div class="flex gap-2 mt-auto">
								<a
									href="/workpapers/{workpaper.id}"
									class="flex-1 px-3 py-1.5 text-xs font-medium text-center bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
								>
									View
								</a>
								{#if workpaper.file_url}
									<a
										href={workpaper.file_url}
										target="_blank"
										class="px-3 py-1.5 text-xs font-medium text-center border border-surface-300 dark:border-surface-600 rounded hover:bg-surface-50 dark:hover:bg-surface-700 transition-colors"
									>
										Download
									</a>
								{/if}
								<button
									onclick={() => handleDelete(workpaper.id)}
									class="px-3 py-1.5 text-xs font-medium text-center text-error-600 dark:text-error-400 border border-error-300 dark:border-error-600 rounded hover:bg-error-50 dark:hover:bg-error-900/20 transition-colors"
								>
									Delete
								</button>
							</div>
						</div>
					{/each}
				</div>
			{:else}
				<div class="text-center py-16">
					<svg class="mx-auto h-16 w-16 text-surface-300 dark:text-surface-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
					<h3 class="text-lg font-medium text-surface-900 dark:text-surface-50 mb-2">No workpapers found</h3>
					<p class="text-surface-500 dark:text-surface-400 mb-6">Try adjusting your search criteria or filters.</p>
				</div>
			{/if}
		</div>
	</div>
{/if}
