<script lang="ts">
	import { onMount } from 'svelte';
	import { listPlans, deletePlan } from './api.js';
	import { listEntities } from '../universe/api.js';
	import { getUsers } from '../universe/users-api.js';

	interface AuditPlan {
		id: number;
		title: string;
		description: string;
		entity: number;
		entity_name: string;
		entity_type: string;
		planned_start: string;
		planned_end: string;
		actual_start?: string | null;
		actual_end?: string | null;
		lead_auditor: number | null;
		lead_auditor_display: string | null;
		auditable_entities_display?: Array<{id: number; name: string; entity_type: string}>;
		audit_team_display?: Array<{user_id: number; role: string; username: string; email: string}>;
		status: string;
		objectives: string;
		scope: string;
		created_at: string;
		updated_at: string;
	}

	interface AuditEntity {
		id: number;
		name: string;
		entity_type: string;
	}

	interface User {
		id: number;
		username: string;
		email: string;
	}

	let plans = $state<AuditPlan[]>([]);
	let entities = $state<AuditEntity[]>([]);
	let users = $state<User[]>([]);
	let loading = $state(true);
	let error = $state('');
	let searchQuery = $state('');
	let filterStatus = $state('');
	let filterEntity = $state('');
	let filterLeadAuditor = $state('');

	function clearFilters() {
		searchQuery = '';
		filterStatus = '';
		filterEntity = '';
		filterLeadAuditor = '';
	}

	// Status choices
	const statusChoices = [
		{ value: '', label: 'All Status' },
		{ value: 'draft', label: '📝 Draft' },
		{ value: 'pending_approval', label: '⏳ Pending Approval' },
		{ value: 'approved', label: '✅ Approved' },
		{ value: 'in_review', label: '🔍 In Review' },
		{ value: 'in_progress', label: '🚀 In Progress' },
		{ value: 'completed', label: '🎉 Completed' },
		{ value: 'cancelled', label: '❌ Cancelled' }
	];

	onMount(async () => {
		await loadData();
	});

	// Watch for search/filter changes to reload data from backend
	$effect(() => {
		if (searchQuery !== undefined || filterStatus !== undefined || filterEntity !== undefined || filterLeadAuditor !== undefined) {
			loadPlans();
		}
	});

	async function loadData() {
		try {
			loading = true;
			error = '';

			// Load entities for filter dropdown
			const entitiesData = await listEntities();
			entities = entitiesData.results || [];

		// Load users for lead auditor filter
		try {
			const usersData = await getUsers();
			users = usersData.results || usersData;
		} catch (err) {
			console.error('Error loading users:', err);
			// Don't fail the entire load if users can't be loaded
			users = [];
		}

			// Load plans with current filters
			await loadPlans();
		} catch (err: any) {
			console.error('Error loading data:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	}

	async function loadPlans() {
		const params: any = {};
		
		if (searchQuery) params.search = searchQuery;
		if (filterStatus) params.status = filterStatus;
		if (filterEntity) params.entity = filterEntity;
		if (filterLeadAuditor) params.lead_auditor = filterLeadAuditor;

		const data = await listPlans(params);
		plans = data.results || [];
	}


	async function handleDelete(plan: AuditPlan) {
		if (!confirm(`Are you sure you want to delete "${plan.title}"? This action cannot be undone.`)) {
			return;
		}

		try {
			await deletePlan(plan.id);
			await loadPlans(); // Refresh the list
		} catch (err: any) {
			console.error('Error deleting plan:', err);
			alert('Failed to delete audit plan. Please try again.');
		}
	}

	function formatDate(dateString: string) {
		return new Date(dateString).toLocaleDateString();
	}

	function getStatusIcon(status: string) {
		const icons: Record<string, string> = {
			draft: '📝',
			pending_approval: '⏳',
			approved: '✅',
			in_review: '🔍',
			in_progress: '🚀',
			completed: '🎉',
			cancelled: '❌'
		};
		return icons[status] || '📋';
	}

	function getStatusColor(status: string) {
		const colors: Record<string, string> = {
			draft: 'text-gray-700 bg-gray-100 dark:text-gray-300 dark:bg-gray-800',
			pending_approval: 'text-orange-700 bg-orange-100 dark:text-orange-300 dark:bg-orange-900',
			approved: 'text-green-700 bg-green-100 dark:text-green-300 dark:bg-green-900',
			in_review: 'text-blue-700 bg-blue-100 dark:text-blue-300 dark:bg-blue-900',
			in_progress: 'text-yellow-700 bg-yellow-100 dark:text-yellow-300 dark:bg-yellow-900',
			completed: 'text-emerald-700 bg-emerald-100 dark:text-emerald-300 dark:bg-emerald-900',
			cancelled: 'text-red-700 bg-red-100 dark:text-red-300 dark:bg-red-900'
		};
		return colors[status] || 'text-gray-700 bg-gray-100 dark:text-gray-300 dark:bg-gray-800';
	}

	function getEntityTypeColor(entityType: string) {
		const colors: Record<string, string> = {
			business_unit: 'text-green-600 bg-green-100',
			division: 'text-teal-600 bg-teal-100',
			function: 'text-orange-600 bg-orange-100',
			section: 'text-cyan-600 bg-cyan-100',
			unit: 'text-lime-600 bg-lime-100',
			process: 'text-yellow-600 bg-yellow-100',
			system: 'text-red-600 bg-red-100',
			vendor: 'text-gray-600 bg-gray-100',
			compliance_domain: 'text-blue-600 bg-blue-100',
			audit_domain: 'text-purple-600 bg-purple-100'
		};
		return colors[entityType] || 'text-gray-600 bg-gray-100';
	}
</script>

<div class="p-6">
	<!-- Header -->
	<div class="mb-8">
		<div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 shadow-xl rounded-xl p-8">
			<div class="flex justify-between items-center">
				<div class="flex items-center gap-4">
					<div class="p-3 bg-white/10 rounded-xl">
						<svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
						</svg>
					</div>
					<div>
						<h1 class="text-3xl font-bold text-white">Audit Plans</h1>
						<p class="text-primary-100 mt-1">Plan and manage audit engagements for entities in your audit universe</p>
					</div>
				</div>
				<a
					href="/audits/planning/new"
					class="inline-flex items-center px-6 py-3 border-2 border-white/30 text-sm font-semibold rounded-xl shadow-lg text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all gap-2"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
					New Audit Plan
				</a>
			</div>
		</div>
	</div>

	<!-- Filters -->
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
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
			<!-- Search -->
			<div>
				<label for="search" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
					🔍 Search
				</label>
				<input
					id="search"
					type="text"
					placeholder="Search plans..."
					bind:value={searchQuery}
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
						<option value={choice.value}>
							{#if choice.value === 'planned'}📅
							{:else if choice.value === 'in_progress'}⏳
							{:else if choice.value === 'completed'}✅
							{:else if choice.value === 'cancelled'}❌
							{/if}
							{choice.label}
						</option>
					{/each}
				</select>
			</div>

			<!-- Entity Filter -->
			<div>
				<label for="entity-filter" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
					🏢 Entity
				</label>
				<select
					id="entity-filter"
					bind:value={filterEntity}
					class="w-full px-4 py-2.5 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
				>
					<option value="">All Entities</option>
					{#each entities as entity}
						<option value={entity.id}>
							{#if entity.entity_type === 'business_unit'}🏢
							{:else if entity.entity_type === 'division'}🔷
							{:else if entity.entity_type === 'function'}⚙️
							{:else if entity.entity_type === 'section'}📑
							{:else if entity.entity_type === 'unit'}📦
							{:else if entity.entity_type === 'process'}🔄
							{:else if entity.entity_type === 'system'}💻
											{:else if entity.entity_type === 'vendor'}🤝
											{:else if entity.entity_type === 'compliance_domain'}📋
											{:else if entity.entity_type === 'audit_domain'}🎯
											{:else}📄
											{/if}
											{entity.name}
										</option>
									{/each}
								</select>
							</div>

			<!-- Lead Auditor Filter -->
			<div>
				<label for="auditor-filter" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
					👤 Lead Auditor
				</label>
				<select
					id="auditor-filter"
					bind:value={filterLeadAuditor}
					class="w-full px-4 py-2.5 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
				>
					<option value="">All Auditors</option>
					{#each users as user}
						<option value={user.id}>{user.username} ({user.email})</option>
					{/each}
				</select>
			</div>
		</div>
	</div>

	<!-- Error State -->
	{#if error}
		<div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-4 mb-6 shadow-sm flex items-start gap-3">
			<svg class="h-5 w-5 text-error-600 dark:text-error-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<div class="text-error-800 dark:text-error-200">Error: {error}</div>
		</div>
	{/if}

	<!-- Loading State -->
	{#if loading}
		<div class="flex justify-center items-center py-16">
			<div class="flex flex-col items-center gap-4">
				<svg class="animate-spin h-12 w-12 text-primary-600" fill="none" viewBox="0 0 24 24">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
				</svg>
				<span class="text-surface-600 dark:text-surface-400 font-medium">Loading audit plans...</span>
			</div>
		</div>
	{:else if plans.length === 0}
		<!-- Empty State -->
		<div class="bg-white dark:bg-surface-800 rounded-xl border-2 border-dashed border-surface-300 dark:border-surface-600 p-12 text-center">
			<svg class="mx-auto h-16 w-16 text-surface-400 dark:text-surface-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
			</svg>
			<h3 class="text-xl font-semibold text-surface-900 dark:text-surface-50 mb-2">No audit plans found</h3>
			<p class="text-surface-600 dark:text-surface-400 mb-6 max-w-md mx-auto">Get started by creating your first audit plan to manage your audit engagements.</p>
			<a
				href="/audits/planning/new"
				class="inline-flex items-center px-6 py-3 border-2 border-transparent text-sm font-semibold rounded-xl shadow-lg text-white bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 transition-all gap-2"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				Create Audit Plan
			</a>
		</div>
	{:else}
		<!-- Plans Table -->
		<div class="bg-white dark:bg-surface-800 shadow-xl rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-surface-200 dark:divide-surface-700">
					<thead>
						<tr class="bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900">
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider">
								📋 Title
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider">
								🏢 Entity
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider">
								👤 Lead Auditor
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider">
								📅 Period
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider">
								📊 Status
							</th>
							<th class="px-6 py-4 text-left text-xs font-bold text-surface-700 dark:text-surface-200 uppercase tracking-wider">
								⚙️ Actions
							</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-surface-200 dark:divide-surface-700">
						{#each plans as plan}
							<tr class="hover:bg-surface-50 dark:hover:bg-surface-700/50 transition-colors">
								<td class="px-6 py-4">
									<div>
										<a
											href="/audits/planning/{plan.id}"
											class="text-sm font-semibold text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 transition-colors"
										>
											{plan.title}
										</a>
										{#if plan.description}
											<p class="text-sm text-surface-600 dark:text-surface-400 truncate max-w-xs mt-1">{plan.description}</p>
										{/if}
									</div>
								</td>
								<td class="px-6 py-4">
									<div class="flex flex-col gap-1">
										<span class="text-sm font-medium text-surface-900 dark:text-surface-50">{plan.entity_name}</span>
										<span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold w-fit {getEntityTypeColor(plan.entity_type)}">
											{#if plan.entity_type === 'business_unit'}🏢
											{:else if plan.entity_type === 'division'}🔷
											{:else if plan.entity_type === 'function'}⚙️
											{:else if plan.entity_type === 'section'}📑
											{:else if plan.entity_type === 'unit'}📦
											{:else if plan.entity_type === 'process'}🔄
											{:else if plan.entity_type === 'system'}💻
											{:else if plan.entity_type === 'vendor'}🤝
											{:else if plan.entity_type === 'compliance_domain'}📋
											{:else if plan.entity_type === 'audit_domain'}🎯
											{:else}📄
											{/if}
											{plan.entity_type.replace('_', ' ')}
										</span>
										{#if plan.auditable_entities_display && plan.auditable_entities_display.length > 0}
											<span class="text-xs text-surface-500 dark:text-surface-400 mt-1">
												+{plan.auditable_entities_display.length} more entit{plan.auditable_entities_display.length === 1 ? 'y' : 'ies'}
											</span>
										{/if}
									</div>
								</td>
								<td class="px-6 py-4">
									<div class="flex flex-col gap-1">
										<span class="text-sm text-surface-900 dark:text-surface-50">
											{plan.lead_auditor_display || '—'}
										</span>
										{#if plan.audit_team_display && plan.audit_team_display.length > 0}
											<span class="text-xs text-surface-500 dark:text-surface-400">
												👥 Team: {plan.audit_team_display.length} member{plan.audit_team_display.length === 1 ? '' : 's'}
											</span>
										{/if}
									</div>
								</td>
								<td class="px-6 py-4">
									<div class="flex flex-col gap-2">
										<!-- Planned Dates -->
										<div class="flex items-center gap-2 text-sm">
											<div class="flex items-center gap-1.5">
												<span class="text-xs text-surface-500 dark:text-surface-400 font-medium">📅 Planned:</span>
												<span class="text-surface-900 dark:text-surface-50 font-medium">{formatDate(plan.planned_start)}</span>
											</div>
											<svg class="w-3 h-3 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
											</svg>
											<div class="flex items-center gap-1.5">
												<span class="text-surface-900 dark:text-surface-50 font-medium">{formatDate(plan.planned_end)}</span>
											</div>
										</div>
										<!-- Actual Dates -->
										{#if plan.actual_start || plan.actual_end}
											<div class="flex items-center gap-2 text-sm">
												<div class="flex items-center gap-1.5">
													<span class="text-xs text-success-600 dark:text-success-400 font-medium">✓ Actual:</span>
													<span class="text-success-700 dark:text-success-300 font-medium">
														{plan.actual_start ? formatDate(plan.actual_start) : '—'}
													</span>
												</div>
												<svg class="w-3 h-3 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
												</svg>
												<div class="flex items-center gap-1.5">
													<span class="text-success-700 dark:text-success-300 font-medium">
														{plan.actual_end ? formatDate(plan.actual_end) : '—'}
													</span>
												</div>
											</div>
										{/if}
									</div>
								</td>
								<td class="px-6 py-4">
									<span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold {getStatusColor(plan.status)}">
										<span class="text-sm">{getStatusIcon(plan.status)}</span>
										<span class="capitalize">{plan.status.replace(/_/g, ' ')}</span>
									</span>
								</td>
								<td class="px-6 py-4">
									<div class="flex items-center gap-2">
										<a
											href="/audits/planning/{plan.id}"
											class="p-2 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
											title="View details"
											aria-label="View plan details"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
											</svg>
										</a>
										<a
											href="/audits/planning/{plan.id}/edit"
											class="p-2 text-surface-600 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-700 rounded-lg transition-colors"
											title="Edit plan"
											aria-label="Edit plan"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
											</svg>
										</a>
										<button
											onclick={() => handleDelete(plan)}
											class="p-2 text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/20 rounded-lg transition-colors"
											title="Delete plan"
											aria-label="Delete plan"
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
		</div>
	{/if}
</div>
