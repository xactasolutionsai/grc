<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { 
		listEngagements, 
		getEngagementSummary,
		getMyEngagements,
		getMyTeamEngagements,
		startEngagement, 
		submitResults, 
		closeEngagement,
		updateProgress,
		deleteEngagement,
		ENGAGEMENT_STATUSES,
		ENGAGEMENT_PRIORITIES,
		AUDIT_TYPES,
		STATUS_COLORS,
		PRIORITY_COLORS,
		canStartEngagement,
		canSubmitResults,
		canCloseEngagement,
		isEngagementOverdue,
		formatEngagementStatus,
		formatEngagementPriority
	} from './api.js';

	export let onEdit = () => {};
	export let onCreate = () => {};

	let engagements = [];
	let loading = true;
	let error = null;
	let searchQuery = '';
	let statusFilter = '';
	let priorityFilter = '';
	let auditTypeFilter = '';
	let auditPlanFilter = '';
	let entityFilter = '';
	let auditorFilter = '';
	let leadFilter = '';
	let showOverdueOnly = false;
	let sortBy = '-created_at';
	let actionLoading = false;
	let deleteConfirmId = null;
	let deleting = false;
	
	// Summary dashboard data
	let summary = {
		total: 0,
		upcoming: 0,
		overdue: 0,
		due_soon: 0,
		in_progress: 0,
		completed_this_month: 0
	};
	let summaryLoading = true;
	
	// Filter tabs
	let activeTab = 'all'; // 'all', 'my_engagements', 'my_team'

	// Pagination
	let currentPage = 1;
	let totalPages = 1;
	let pageSize = 20;

	onMount(async () => {
		// Read filters from URL params
		const params = $page.url.searchParams;
		if (params.has('status')) statusFilter = params.get('status') || '';
		if (params.has('priority')) priorityFilter = params.get('priority') || '';
		if (params.has('audit_type')) auditTypeFilter = params.get('audit_type') || '';
		
		await Promise.all([loadSummary(), loadEngagements()]);
	});

	// Watch for search/filter changes to reload data from backend
	$: if (searchQuery !== undefined || statusFilter !== undefined || priorityFilter !== undefined || 
		auditTypeFilter !== undefined || auditPlanFilter !== undefined || entityFilter !== undefined || 
		auditorFilter !== undefined || leadFilter !== undefined || showOverdueOnly !== undefined) {
		loadEngagements();
	}
	
	// Watch for tab changes
	$: if (activeTab !== undefined) {
		loadEngagements();
	}

	async function loadSummary() {
		summaryLoading = true;
		try {
			const data = await getEngagementSummary();
			summary = data;
		} catch (err) {
			console.error('Error loading summary:', err);
		} finally {
			summaryLoading = false;
		}
	}

	async function loadEngagements() {
		loading = true;
		error = null;
		
		try {
			const params = {
				page: currentPage,
				page_size: pageSize,
				ordering: sortBy
			};

			if (searchQuery) params.search = searchQuery;
			if (statusFilter) params.status = statusFilter;
			if (priorityFilter) params.priority = priorityFilter;
			if (auditTypeFilter) params.audit_type = auditTypeFilter;
			if (auditPlanFilter) params.audit_plan = auditPlanFilter;
			if (entityFilter) params.entity = entityFilter;
			if (auditorFilter) params.assigned_auditor = auditorFilter;
			if (leadFilter) params.engagement_lead = leadFilter;
			if (showOverdueOnly) params.overdue = 'true';
			
			// Handle filter tabs
			if (activeTab === 'my_engagements') {
				params.my_engagements = 'true';
			} else if (activeTab === 'my_team') {
				params.my_team = 'true';
			}

			const data = await listEngagements(params);
			engagements = data.results || data;
			totalPages = Math.ceil((data.count || engagements.length) / pageSize);
			loading = false;
		} catch (err) {
			console.error('Error loading engagements:', err);
			error = err.message;
			loading = false;
		}
	}


	async function handleSort(field) {
		if (sortBy === field) {
			sortBy = `-${field}`;
		} else {
			sortBy = field;
		}
		await loadEngagements();
	}

	async function handlePageChange(page) {
		currentPage = page;
		await loadEngagements();
	}

	async function handleAction(action, engagement) {
		actionLoading = true;
		try {
			switch (action) {
				case 'start':
					await startEngagement(engagement.id);
					break;
				case 'submit':
					await submitResults(engagement.id, {
						findings_summary: engagement.findings_summary || '',
						recommendations: engagement.recommendations || ''
					});
					break;
				case 'close':
					await closeEngagement(engagement.id, {
						closure_notes: engagement.closure_notes || ''
					});
					break;
			}
			await loadEngagements();
		} catch (err) {
			console.error(`Error ${action}ing engagement:`, err);
			error = err.message;
		} finally {
			actionLoading = false;
		}
	}

	async function handleProgressUpdate(engagement, progress) {
		actionLoading = true;
		try {
			await updateProgress(engagement.id, { progress_percentage: progress });
			await loadEngagements();
		} catch (err) {
			console.error('Error updating progress:', err);
			error = err.message;
		} finally {
			actionLoading = false;
		}
	}

	function formatDate(dateString) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleDateString();
	}

	async function handleDelete(engagementId) {
		deleting = true;
		try {
			await deleteEngagement(engagementId);
			await loadEngagements();
			deleteConfirmId = null;
		} catch (err) {
			console.error('Error deleting engagement:', err);
			error = err.message;
		} finally {
			deleting = false;
		}
	}

	function confirmDelete(engagementId) {
		deleteConfirmId = engagementId;
	}

	function cancelDelete() {
		deleteConfirmId = null;
	}

	function formatDateTime(dateString) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleString();
	}

	function getStatusColor(status) {
		const colorMap = {
			gray: 'bg-gray-100 text-gray-800',
			blue: 'bg-blue-100 text-blue-800',
			yellow: 'bg-yellow-100 text-yellow-800',
			orange: 'bg-orange-100 text-orange-800',
			green: 'bg-green-100 text-green-800',
			red: 'bg-red-100 text-red-800'
		};
		return colorMap[STATUS_COLORS[status]] || 'bg-gray-100 text-gray-800';
	}

	function getPriorityColor(priority) {
		const colorMap = {
			green: 'bg-green-100 text-green-800',
			yellow: 'bg-yellow-100 text-yellow-800',
			orange: 'bg-orange-100 text-orange-800',
			red: 'bg-red-100 text-red-800'
		};
		return colorMap[PRIORITY_COLORS[priority]] || 'bg-gray-100 text-gray-800';
	}

	function getProgressColor(percentage) {
		if (percentage >= 100) return 'bg-green-500';
		if (percentage >= 75) return 'bg-blue-500';
		if (percentage >= 50) return 'bg-yellow-500';
		if (percentage >= 25) return 'bg-orange-500';
		return 'bg-red-500';
	}

	function clearFilters() {
		searchQuery = '';
		statusFilter = '';
		priorityFilter = '';
		auditTypeFilter = '';
		auditPlanFilter = '';
		entityFilter = '';
		auditorFilter = '';
		leadFilter = '';
		showOverdueOnly = false;
	}
	
	function handleTabChange(tab) {
		activeTab = tab;
		currentPage = 1; // Reset to first page when changing tabs
	}
</script>

<div class="p-6">
	<!-- Header Card -->
	<div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 shadow-xl rounded-xl mb-8 p-8">
		<div class="flex justify-between items-center">
			<div class="flex items-center gap-4">
				<div class="p-3 bg-white/10 rounded-xl">
					<svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
				</div>
				<div>
					<h1 class="text-3xl font-bold text-white">Audit Engagements</h1>
					<p class="text-primary-100 mt-1">Manage and track audit engagement activities</p>
				</div>
			</div>
			<button 
				on:click={onCreate}
				class="inline-flex items-center gap-2 px-6 py-3 border-2 border-white/30 text-sm font-semibold rounded-xl shadow-lg text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				Create Engagement
			</button>
		</div>
	</div>

	<!-- Summary Dashboard -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Total</p>
					<p class="text-3xl font-bold text-surface-900 dark:text-surface-50 mt-1">
						{summaryLoading ? '...' : summary.total}
					</p>
				</div>
				<div class="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
					<svg class="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
				</div>
			</div>
		</div>

		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Upcoming</p>
					<p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1">
						{summaryLoading ? '...' : summary.upcoming}
					</p>
				</div>
				<div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
					<svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
					</svg>
				</div>
			</div>
		</div>

		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Overdue</p>
					<p class="text-3xl font-bold text-error-600 dark:text-error-400 mt-1">
						{summaryLoading ? '...' : summary.overdue}
					</p>
				</div>
				<div class="p-3 bg-error-100 dark:bg-error-900/30 rounded-lg">
					<svg class="w-6 h-6 text-error-600 dark:text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
			</div>
		</div>

		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Due Soon</p>
					<p class="text-3xl font-bold text-warning-600 dark:text-warning-400 mt-1">
						{summaryLoading ? '...' : summary.due_soon}
					</p>
				</div>
				<div class="p-3 bg-warning-100 dark:bg-warning-900/30 rounded-lg">
					<svg class="w-6 h-6 text-warning-600 dark:text-warning-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
			</div>
		</div>

		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-surface-600 dark:text-surface-400">In Progress</p>
					<p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1">
						{summaryLoading ? '...' : summary.in_progress}
					</p>
				</div>
				<div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
					<svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
					</svg>
				</div>
			</div>
		</div>

		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-surface-600 dark:text-surface-400">Completed</p>
					<p class="text-3xl font-bold text-success-600 dark:text-success-400 mt-1">
						{summaryLoading ? '...' : summary.completed_this_month}
					</p>
				</div>
				<div class="p-3 bg-success-100 dark:bg-success-900/30 rounded-lg">
					<svg class="w-6 h-6 text-success-600 dark:text-success-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
			</div>
		</div>
	</div>

	<!-- Filter Tabs -->
	<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-2 mb-6">
		<div class="flex gap-2">
			<button
				on:click={() => handleTabChange('all')}
				class="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all {activeTab === 'all' ? 'bg-primary-600 text-white shadow-md' : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700'}"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
				</svg>
				All Engagements
			</button>
			<button
				on:click={() => handleTabChange('my_engagements')}
				class="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all {activeTab === 'my_engagements' ? 'bg-primary-600 text-white shadow-md' : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700'}"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
				</svg>
				My Engagements
			</button>
			<button
				on:click={() => handleTabChange('my_team')}
				class="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all {activeTab === 'my_team' ? 'bg-primary-600 text-white shadow-md' : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700'}"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
				</svg>
				My Team's Engagements
			</button>
		</div>
	</div>

	<!-- Filters and Search -->
	<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6 mb-6">
		<div class="flex items-center justify-between mb-4">
			<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50">Filters</h2>
			<button
				on:click={clearFilters}
				class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-surface-700 dark:text-surface-300 bg-surface-100 dark:bg-surface-700 hover:bg-surface-200 dark:hover:bg-surface-600 rounded-lg transition-colors"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
				Clear Filters
			</button>
		</div>
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
			<!-- Search -->
			<div>
				<label for="search-input" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
					🔍 Search
				</label>
				<input
					id="search-input"
					type="text"
					bind:value={searchQuery}
					placeholder="Search engagements..."
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
					bind:value={statusFilter}
					class="w-full px-4 py-2.5 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
				>
					<option value="">All Statuses</option>
					{#each ENGAGEMENT_STATUSES as status}
						<option value={status.value}>{status.label}</option>
					{/each}
				</select>
			</div>

			<!-- Priority Filter -->
			<div>
				<label for="priority-filter" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
					⚡ Priority
				</label>
				<select
					id="priority-filter"
					bind:value={priorityFilter}
					class="w-full px-4 py-2.5 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
				>
					<option value="">All Priorities</option>
					{#each ENGAGEMENT_PRIORITIES as priority}
						<option value={priority.value}>{priority.label}</option>
					{/each}
				</select>
			</div>

			<!-- Audit Type Filter -->
			<div>
				<label for="audit-type-filter" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
					🔍 Audit Type
				</label>
				<select
					id="audit-type-filter"
					bind:value={auditTypeFilter}
					class="w-full px-4 py-2.5 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
				>
					<option value="">All Types</option>
					{#each AUDIT_TYPES as auditType}
						<option value={auditType.value}>{auditType.label}</option>
					{/each}
				</select>
			</div>

			<!-- Overdue Filter -->
			<div class="flex items-end">
				<label for="overdue-filter" class="flex items-center gap-2 px-4 py-2.5 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 rounded-xl cursor-pointer hover:bg-surface-50 dark:hover:bg-surface-700 transition-colors w-full">
					<input
						id="overdue-filter"
						type="checkbox"
						bind:checked={showOverdueOnly}
						class="w-4 h-4 text-primary-600 border-surface-300 rounded focus:ring-primary-500"
					/>
					<span class="text-sm font-semibold text-surface-900 dark:text-surface-50">⏰ Overdue Only</span>
				</label>
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
				<span class="text-surface-600 dark:text-surface-400 font-medium">Loading engagements...</span>
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
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider cursor-pointer hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors whitespace-nowrap"
								on:click={() => handleSort('title')}>
								📋 Title
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
								📑 Audit Plan
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
								🏢 Entity
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider cursor-pointer hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors whitespace-nowrap"
								on:click={() => handleSort('status')}>
								📊 Status
							</th>
						<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider cursor-pointer hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors whitespace-nowrap"
							on:click={() => handleSort('priority')}>
							⚡ Priority
						</th>
						<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider cursor-pointer hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors whitespace-nowrap"
							on:click={() => handleSort('audit_type')}>
							🔍 Type
						</th>
						<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
							👤 Auditor
						</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider cursor-pointer hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors whitespace-nowrap"
								on:click={() => handleSort('planned_start_date')}>
								📅 Start
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider cursor-pointer hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors whitespace-nowrap"
								on:click={() => handleSort('planned_end_date')}>
								📅 End
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider cursor-pointer hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors whitespace-nowrap"
								on:click={() => handleSort('progress_percentage')}>
								📈 Progress
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider whitespace-nowrap">
								⚙️ Actions
							</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-surface-200 dark:divide-surface-700">
						{#each engagements as engagement}
							<tr class="hover:bg-surface-50 dark:hover:bg-surface-700/50 transition-colors {isEngagementOverdue(engagement) ? 'bg-error-50 dark:bg-error-900/20' : ''}">
								<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
									<div class="font-semibold truncate" title="{engagement.title}">{engagement.title}</div>
									{#if engagement.description}
										<div class="text-xs text-surface-600 dark:text-surface-400 truncate" title="{engagement.description}">{engagement.description}</div>
									{/if}
									{#if isEngagementOverdue(engagement)}
										<div class="text-xs text-error-600 dark:text-error-400 font-semibold">⚠️ OVERDUE</div>
									{/if}
								</td>
								<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
									<div class="truncate" title="{engagement.audit_plan_title || '—'}">{engagement.audit_plan_title || '—'}</div>
								</td>
								<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
									<div class="truncate" title="{engagement.entity_name || '—'}">{engagement.entity_name || '—'}</div>
								</td>
								<td class="px-6 py-4">
									<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap {getStatusColor(engagement.status)}">
										{formatEngagementStatus(engagement.status)}
									</span>
								</td>
							<td class="px-6 py-4">
								<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap {getPriorityColor(engagement.priority)}">
									{formatEngagementPriority(engagement.priority)}
								</span>
							</td>
							<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
								<div class="truncate" title="{AUDIT_TYPES.find(t => t.value === engagement.audit_type)?.label || engagement.audit_type || '—'}">
									{AUDIT_TYPES.find(t => t.value === engagement.audit_type)?.label || engagement.audit_type || '—'}
								</div>
							</td>
							<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
								<div class="truncate" title="{engagement.assigned_auditor_display || '—'}">{engagement.assigned_auditor_display || '—'}</div>
							</td>
								<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
									<div class="space-y-1">
										<div class="flex items-center gap-1">
											<span class="text-surface-500 dark:text-surface-400 text-xs">Plan:</span>
											<span>{formatDate(engagement.planned_start_date)}</span>
										</div>
										{#if engagement.actual_start_date}
											<div class="flex items-center gap-1">
												<span class="text-success-600 dark:text-success-400 text-xs font-semibold">Actual:</span>
												<span class="text-success-600 dark:text-success-400 font-medium">{formatDate(engagement.actual_start_date)}</span>
											</div>
										{/if}
									</div>
								</td>
								<td class="px-6 py-4 text-sm text-surface-900 dark:text-surface-50">
									<div class="space-y-1">
										<div class="flex items-center gap-1">
											<span class="text-surface-500 dark:text-surface-400 text-xs">Plan:</span>
											<span>{formatDate(engagement.planned_end_date)}</span>
										</div>
										{#if engagement.actual_end_date}
											<div class="flex items-center gap-1">
												<span class="text-success-600 dark:text-success-400 text-xs font-semibold">Actual:</span>
												<span class="text-success-600 dark:text-success-400 font-medium">{formatDate(engagement.actual_end_date)}</span>
											</div>
										{/if}
									</div>
								</td>
								<td class="px-6 py-4">
									<div class="flex items-center gap-2">
										<div class="flex-1 bg-surface-200 dark:bg-surface-700 rounded-full h-2">
											<div 
												class="h-2 rounded-full {getProgressColor(engagement.progress_percentage)}"
												style="width: {engagement.progress_percentage}%"
											></div>
										</div>
										<span class="text-xs font-semibold text-surface-900 dark:text-surface-50 min-w-[3rem] text-right">{engagement.progress_percentage}%</span>
									</div>
								</td>
								<td class="px-6 py-4">
									<div class="flex items-center gap-2">
										{#if canStartEngagement(engagement)}
											<button
												on:click={() => handleAction('start', engagement)}
												disabled={actionLoading}
												class="p-2 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors disabled:opacity-50"
												title="Start engagement"
												aria-label="Start engagement"
											>
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
												</svg>
											</button>
										{/if}
										{#if canSubmitResults(engagement)}
											<button
												on:click={() => handleAction('submit', engagement)}
												disabled={actionLoading}
												class="p-2 text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors disabled:opacity-50"
												title="Submit results"
												aria-label="Submit results"
											>
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
												</svg>
											</button>
										{/if}
										{#if canCloseEngagement(engagement)}
											<button
												on:click={() => handleAction('close', engagement)}
												disabled={actionLoading}
												class="p-2 text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-lg transition-colors disabled:opacity-50"
												title="Close engagement"
												aria-label="Close engagement"
											>
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
												</svg>
											</button>
										{/if}
										<button
											on:click={() => goto(`/audits/engagements/${engagement.id}`)}
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
											on:click={() => confirmDelete(engagement.id)}
											class="p-2 text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/20 rounded-lg transition-colors"
											title="Delete engagement"
											aria-label="Delete engagement"
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
			
			{#if engagements.length === 0}
				<div class="text-center py-12 px-4">
					<svg class="mx-auto h-16 w-16 text-surface-400 dark:text-surface-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
					<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-2">No engagements found</h3>
					<p class="text-surface-600 dark:text-surface-400">Create your first engagement to get started.</p>
				</div>
			{/if}
		</div>

		<!-- Pagination -->
		{#if totalPages > 1}
			<div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4">
				<div class="flex-1 flex justify-between sm:hidden">
					<button
						on:click={() => handlePageChange(currentPage - 1)}
						disabled={currentPage <= 1}
						class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
					>
						Previous
					</button>
					<button
						on:click={() => handlePageChange(currentPage + 1)}
						disabled={currentPage >= totalPages}
						class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
					>
						Next
					</button>
				</div>
				<div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
					<div>
						<p class="text-sm text-gray-700">
							Showing page <span class="font-medium">{currentPage}</span> of <span class="font-medium">{totalPages}</span>
						</p>
					</div>
					<div>
						<nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
							{#each Array(totalPages) as _, i}
								<button
									on:click={() => handlePageChange(i + 1)}
									class="relative inline-flex items-center px-4 py-2 border text-sm font-medium {i + 1 === currentPage ? 'z-10 bg-blue-50 border-blue-500 text-blue-600' : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'}"
								>
									{i + 1}
								</button>
							{/each}
						</nav>
					</div>
				</div>
			</div>
		{/if}
	{/if}

	<!-- Delete Confirmation Modal -->
	{#if deleteConfirmId}
		<div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
			<div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
				<div class="mt-3 text-center">
					<div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
						<svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
						</svg>
					</div>
					<h3 class="text-lg font-medium text-gray-900 mt-4">Delete Engagement</h3>
					<div class="mt-2 px-7 py-3">
						<p class="text-sm text-gray-500">
							Are you sure you want to delete this engagement? This action cannot be undone.
						</p>
					</div>
					<div class="items-center px-4 py-3">
						<button
							on:click={() => handleDelete(deleteConfirmId)}
							disabled={deleting}
							class="px-4 py-2 bg-red-600 text-white text-base font-medium rounded-md w-24 mr-2 shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-300 disabled:opacity-50"
						>
							{deleting ? 'Deleting...' : 'Delete'}
						</button>
						<button
							on:click={cancelDelete}
							disabled={deleting}
							class="px-4 py-2 bg-gray-300 text-gray-800 text-base font-medium rounded-md w-24 shadow-sm hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-300 disabled:opacity-50"
						>
							Cancel
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

