<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { listEntities } from './api.js';
	import TreeEntityRow from './TreeEntityRow.svelte';
	import OrganizationalStructure from './OrganizationalStructure.svelte';
	// Skeleton UI components removed - using regular HTML elements with Skeleton UI styling

	export let refreshTrigger = 0;

	let entities: any[] = [];
	let filteredEntities: any[] = [];
	let treeEntities: any[] = [];
	let loading = true;
	let error: string | null = null;
	let searchQuery = '';
	let filterType = '';
	let filterStatus = '';
	let filterPriority = '';
	let filterCriticality = '';
	let filterCountry = '';
	let filterRegion = '';
	let activeView = 'table'; // 'table' or 'hierarchy'
	let activeTab = 'all'; // 'all', 'my_entities', 'my_team'
	let mounted = false;

	onMount(() => {
		// Read filters from URL params
		const params = $page.url.searchParams;
		if (params.has('entity_type')) filterType = params.get('entity_type') || '';
		if (params.has('criticality')) filterCriticality = params.get('criticality') || '';
		if (params.has('priority')) filterPriority = params.get('priority') || '';
		if (params.has('country')) filterCountry = params.get('country') || '';
		if (params.has('region')) filterRegion = params.get('region') || '';

		mounted = true;
		loadEntities();

		// Listen for entity deletion events from child components
		const handleEntityDeletedEvent = (event: Event) => {
			const customEvent = event as CustomEvent;
			handleEntityDeleted(customEvent);
		};

		window.addEventListener('entityDeleted', handleEntityDeletedEvent);

		return () => {
			window.removeEventListener('entityDeleted', handleEntityDeletedEvent);
		};
	});

	// Watch for refresh trigger changes
	$: if (refreshTrigger > 0) {
		loadEntities();
	}

	// Watch for search/filter changes to reload data from backend
	$: {
		// This will trigger whenever any of these values change
		searchQuery;
		filterType;
		filterStatus;
		filterPriority;
		filterCriticality;
		filterCountry;
		filterRegion;

		// Load entities when filters change (but skip the initial mount)
		if (mounted) {
			loadEntities();
		}
	}

	// Watch for tab changes
	$: if (activeTab !== undefined) {
		if (mounted) {
			loadEntities();
		}
	}

	// Watch for entities changes to rebuild tree (no client-side filtering needed)
	$: if (entities.length >= 0) {
		filteredEntities = entities; // No filtering needed - backend handles it
		treeEntities = buildTree(filteredEntities);
	}

	// Watch for view changes to refresh hierarchy
	$: if (activeView === 'hierarchy') {
		refreshTrigger += 1;
	}

	function handleEntityDeleted(event: CustomEvent) {
		// Remove the deleted entity from the entities array
		entities = entities.filter(entity => entity.id !== event.detail.id);
		// Rebuild the tree
		filteredEntities = entities;
		treeEntities = buildTree(filteredEntities);
	}


	function buildTree(entities: any[]): any[] {
		const lookup: Record<number, any> = {};
		const roots: any[] = [];

		// Step 1: Initialize lookup
		entities.forEach(e => {
			lookup[e.id] = { ...e, children: [] };
		});

		// Step 2: Assign children to parents
		entities.forEach(e => {
			if (e.parent) {
				// Attach to parent if parent exists in filtered results
				if (lookup[e.parent]) {
					lookup[e.parent].children.push(lookup[e.id]);
				} else {
					// Parent not in filtered results, show as root
					// This allows child entities to be visible even when parent is filtered out
					roots.push(lookup[e.id]);
				}
			} else {
				// Root entity (no parent)
				roots.push(lookup[e.id]);
			}
		});

		return roots;
	}

	async function loadEntities() {
		try {
			loading = true;
			error = null;
			// Pass search and filter parameters to backend
			const params: Record<string, any> = {};
			if (searchQuery) params.search = searchQuery;
			if (filterType) params.entity_type = filterType;
			if (filterStatus) params.is_active = filterStatus === 'active';
			if (filterPriority) params.priority = filterPriority;
			if (filterCriticality) params.criticality = filterCriticality;
			if (filterCountry) params.country = filterCountry;
			if (filterRegion) params.region = filterRegion;

			// Handle filter tabs
			if (activeTab === 'my_entities') {
				params.my_entities = 'true';
			} else if (activeTab === 'my_team') {
				params.my_team = 'true';
			}

			const data = await listEntities(params);
			entities = data.results || data;
		} catch (err: any) {
			console.error('Error loading entities:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	}

	function formatEntityType(type: string) {
		return type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
	}

	function formatDate(dateString: string | null) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleDateString();
	}

	function formatDateTime(dateString: string | null) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleString();
	}

	function handleTabChange(tab: string) {
		activeTab = tab;
	}

</script>

	{#if loading}
		<div class="flex justify-center items-center py-12">
			<div class="flex flex-col items-center gap-3">
				<svg class="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
				</svg>
				<div class="text-surface-600 font-medium">Loading audit universe...</div>
			</div>
		</div>
	{:else if error}
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
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
				</svg>
				All Entities
			</button>
			<button
				onclick={() => handleTabChange('my_entities')}
				class="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all {activeTab === 'my_entities' ? 'bg-primary-600 text-white shadow-md' : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700'}"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
				</svg>
				My Entities
			</button>
			<button
				onclick={() => handleTabChange('my_team')}
				class="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all {activeTab === 'my_team' ? 'bg-primary-600 text-white shadow-md' : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700'}"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
				</svg>
				My Team's Entities
			</button>
			</div>
		</div>

		<!-- View Toggle -->
		<div class="mb-6 flex items-center justify-between">
			<div class="bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg p-1 inline-flex shadow-sm">
				<button
					onclick={() => activeView = 'table'}
					class="px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 flex items-center gap-2 {activeView === 'table' ? 'bg-primary-600 text-white shadow-sm' : 'text-surface-600 dark:text-surface-300 hover:text-surface-900 dark:hover:text-surface-50 hover:bg-surface-50 dark:hover:bg-surface-700'}"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
					</svg>
					Table View
				</button>
				<button
					onclick={() => activeView = 'hierarchy'}
					class="px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 flex items-center gap-2 {activeView === 'hierarchy' ? 'bg-primary-600 text-white shadow-sm' : 'text-surface-600 dark:text-surface-300 hover:text-surface-900 dark:hover:text-surface-50 hover:bg-surface-50 dark:hover:bg-surface-700'}"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
					</svg>
					Organizational Structure
				</button>
			</div>

			<div class="text-sm text-surface-500 dark:text-surface-400">
				<span class="font-medium text-surface-900 dark:text-surface-50">{filteredEntities.length}</span> {filteredEntities.length === 1 ? 'entity' : 'entities'}
			</div>
		</div>

	{#if activeView === 'hierarchy'}
		<OrganizationalStructure {refreshTrigger} {activeTab} />
	{:else}
		<div class="bg-white dark:bg-surface-900 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
			<!-- Search and Filters -->
			<div class="bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 px-6 py-5 border-b border-surface-200 dark:border-surface-700">
				<div class="flex flex-col gap-4">
					<!-- First Row: Search and Basic Filters -->
					<div class="flex flex-col sm:flex-row gap-3">
						<!-- Search Input -->
						<div class="flex-1 relative">
							<svg class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
							<input
								type="text"
								placeholder="Search entities..."
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
								<option value="business_unit">🏢 Business Unit</option>
								<option value="division">🔷 Division</option>
								<option value="function">⚙️ Function</option>
								<option value="section">📑 Section</option>
								<option value="unit">📦 Unit</option>
								<option value="process">🔄 Process</option>
								<option value="system">💻 System</option>
								<option value="vendor">🤝 Vendor</option>
								<option value="compliance_domain">📋 Compliance Domain</option>
								<option value="audit_domain">🎯 Audit Domain</option>
							</select>
						</div>

						<!-- Status Filter -->
						<div class="sm:w-36">
							<select
								bind:value={filterStatus}
								class="w-full px-4 py-2.5 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-50"
							>
								<option value="">All Status</option>
								<option value="active">✅ Active</option>
								<option value="inactive">⏸️ Inactive</option>
							</select>
						</div>

					<div class="sm:w-36">
						<select
							bind:value={filterPriority}
							class="w-full px-4 py-2.5 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-50"
						>
							<option value="">All Priority</option>
							<option value="low">🟢 Low</option>
							<option value="medium">🟡 Medium</option>
							<option value="high">🟠 High</option>
							<option value="critical">🔴 Critical</option>
						</select>
					</div>

					<div class="sm:w-36">
						<select
							bind:value={filterCriticality}
							class="w-full px-4 py-2.5 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-50"
						>
							<option value="">All Criticality</option>
							<option value="High">🔴 High</option>
							<option value="Medium">🟡 Medium</option>
							<option value="Low">🟢 Low</option>
						</select>
					</div>
				</div>

					<!-- Second Row: Geographical Filters -->
					<div class="flex flex-col sm:flex-row gap-3">
						<!-- Country Filter -->
						<div class="sm:w-52">
							<select
								bind:value={filterCountry}
								class="w-full px-4 py-2.5 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-50"
							>
								<option value="">🌍 All Countries</option>
								<option value="United States">🇺🇸 United States</option>
								<option value="Canada">🇨🇦 Canada</option>
								<option value="United Kingdom">🇬🇧 United Kingdom</option>
								<option value="Germany">🇩🇪 Germany</option>
								<option value="France">🇫🇷 France</option>
								<option value="Japan">🇯🇵 Japan</option>
								<option value="China">🇨🇳 China</option>
								<option value="India">🇮🇳 India</option>
								<option value="Australia">🇦🇺 Australia</option>
								<option value="Brazil">🇧🇷 Brazil</option>
								<option value="Mexico">🇲🇽 Mexico</option>
								<option value="Singapore">🇸🇬 Singapore</option>
								<option value="Netherlands">🇳🇱 Netherlands</option>
								<option value="Switzerland">🇨🇭 Switzerland</option>
							</select>
						</div>

						<!-- Region Filter -->
						<div class="flex-1">
							<div class="relative">
								<svg class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
								</svg>
								<input
									type="text"
									placeholder="Filter by region/state..."
									bind:value={filterRegion}
									class="w-full pl-10 pr-4 py-2.5 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-50 placeholder-surface-400"
								/>
							</div>
						</div>

						<!-- Clear Filters Button -->
						<div class="sm:w-36">
						<button
							onclick={() => {
								searchQuery = '';
								filterType = '';
								filterStatus = '';
								filterPriority = '';
								filterCriticality = '';
								filterCountry = '';
								filterRegion = '';
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

			<!-- Entities List -->
			<div class="p-6">
				{#if treeEntities.length > 0}
					<!-- Accordion Style List -->
					<div class="space-y-3">
						{#each treeEntities as node}
							<TreeEntityRow {node} level={0} />
						{/each}
					</div>
				{:else if entities.length === 0}
					<div class="text-center py-16">
						<svg class="mx-auto h-16 w-16 text-surface-300 dark:text-surface-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
						</svg>
						<h3 class="text-lg font-medium text-surface-900 dark:text-surface-50 mb-2">No audit entities yet</h3>
						<p class="text-surface-500 dark:text-surface-400 mb-6">Create your first entity to start building your audit universe.</p>
					</div>
				{:else}
					<div class="text-center py-16">
						<svg class="mx-auto h-16 w-16 text-surface-300 dark:text-surface-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
						</svg>
						<h3 class="text-lg font-medium text-surface-900 dark:text-surface-50 mb-2">No matching entities</h3>
						<p class="text-surface-500 dark:text-surface-400 mb-6">Try adjusting your search criteria or filters.</p>
					</div>
				{/if}
			</div>
		</div>
	{/if}
{/if}
