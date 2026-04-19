<script lang="ts">
	import { onMount } from 'svelte';
	import { getPlan, updatePlan, deletePlan } from './api.js';

	interface AuditPlan {
		id: number;
		title: string;
		description: string;
		entity: number;
		entity_name: string;
		entity_type: string;
		planned_start: string;
		planned_end: string;
		lead_auditor: number | null;
		lead_auditor_display: string | null;
		status: string;
		objectives: string;
		scope: string;
		resources: any;
		created_at: string;
		updated_at: string;
	}

	// Props
	let { planId }: { planId: number } = $props();

	// State
	let plan = $state<AuditPlan | null>(null);
	let loading = $state(true);
	let error = $state('');
	let showEditModal = $state(false);
	let editing = $state(false);

	// Edit form
	let editForm = $state<Partial<AuditPlan>>({});

	// Status choices
	const statusChoices = [
		{ value: 'planned', label: 'Planned' },
		{ value: 'in_progress', label: 'In Progress' },
		{ value: 'completed', label: 'Completed' },
		{ value: 'cancelled', label: 'Cancelled' }
	];

	onMount(async () => {
		await loadPlan();
	});

	async function loadPlan() {
		try {
			loading = true;
			error = '';
			plan = await getPlan(planId);
		} catch (err: any) {
			console.error('Error loading plan:', err);
			error = err.message || 'Failed to load audit plan';
		} finally {
			loading = false;
		}
	}

	function openEditModal() {
		if (!plan) return;
		
		editForm = {
			entity: plan.entity,
			title: plan.title,
			description: plan.description,
			planned_start: plan.planned_start,
			planned_end: plan.planned_end,
			lead_auditor: plan.lead_auditor,
			status: plan.status,
			objectives: plan.objectives,
			scope: plan.scope,
			resources: plan.resources
		};
		showEditModal = true;
	}

	function closeEditModal() {
		showEditModal = false;
		editForm = {};
	}

	async function savePlan() {
		if (!plan) return;

		try {
			editing = true;

			// Validate required fields
			if (!editForm.title?.trim()) {
				alert('Title is required');
				return;
			}
			if (!editForm.planned_start) {
				alert('Planned start date is required');
				return;
			}
			if (!editForm.planned_end) {
				alert('Planned end date is required');
				return;
			}
			if (new Date(editForm.planned_end) < new Date(editForm.planned_start)) {
				alert('Planned end date must be after planned start date');
				return;
			}

			// Prepare complete data for API
			const planData = {
				entity: editForm.entity,
				title: editForm.title.trim(),
				description: editForm.description?.trim() || '',
				planned_start: editForm.planned_start,
				planned_end: editForm.planned_end,
				lead_auditor: editForm.lead_auditor,
				status: editForm.status,
				objectives: editForm.objectives?.trim() || '',
				scope: editForm.scope?.trim() || '',
				resources: editForm.resources
			};

			await updatePlan(plan.id, planData);
			await loadPlan(); // Refresh the plan
			closeEditModal();
		} catch (err: any) {
			console.error('Error updating plan:', err);
			alert('Failed to update audit plan. Please try again.');
		} finally {
			editing = false;
		}
	}

	async function handleDelete() {
		if (!plan) return;

		if (!confirm(`Are you sure you want to delete "${plan.title}"? This action cannot be undone.`)) {
			return;
		}

		try {
			await deletePlan(plan.id);
			// Redirect to plans list
			window.location.href = '/audits/planning';
		} catch (err: any) {
			console.error('Error deleting plan:', err);
			alert('Failed to delete audit plan. Please try again.');
		}
	}

	function formatDate(dateString: string) {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function formatDateTime(dateString: string) {
		return new Date(dateString).toLocaleString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function getStatusColor(status: string) {
		const colors: Record<string, string> = {
			planned: 'text-blue-600 bg-blue-100',
			in_progress: 'text-yellow-600 bg-yellow-100',
			completed: 'text-green-600 bg-green-100',
			cancelled: 'text-red-600 bg-red-100'
		};
		return colors[status] || 'text-gray-600 bg-gray-100';
	}

	function getEntityTypeColor(entityType: string) {
		const colors: Record<string, string> = {
			business_unit: 'text-green-600 bg-green-100',
			process: 'text-yellow-600 bg-yellow-100',
			system: 'text-red-600 bg-red-100',
			vendor: 'text-gray-600 bg-gray-100',
			compliance_domain: 'text-blue-600 bg-blue-100'
		};
		return colors[entityType] || 'text-gray-600 bg-gray-100';
	}

	function getDuration() {
		if (!plan) return '';
		const start = new Date(plan.planned_start);
		const end = new Date(plan.planned_end);
		const diffTime = Math.abs(end.getTime() - start.getTime());
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
		return `${diffDays} day${diffDays !== 1 ? 's' : ''}`;
	}
</script>

<div class="mx-auto p-6">
	<!-- Header Card -->
	{#if plan}
		<div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 shadow-xl rounded-xl mb-8 overflow-hidden">
			<div class="p-8">
				<div class="flex justify-between items-start">
					<div class="flex-1">
						<div class="flex items-center gap-3 mb-3">
							<div class="p-3 bg-white/10 rounded-xl">
								<svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
								</svg>
							</div>
							<div>
								<h1 class="text-3xl font-bold text-white">{plan.title}</h1>
								<p class="text-primary-100 mt-1">Audit Plan Details</p>
							</div>
						</div>
						<div class="flex items-center gap-3 mt-4">
							<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-white/20 text-white backdrop-blur-sm">
								{#if plan.status === 'planned'}📅
								{:else if plan.status === 'in_progress'}⏳
								{:else if plan.status === 'completed'}✅
								{:else if plan.status === 'cancelled'}❌
								{/if}
								{plan.status.replace('_', ' ')}
							</span>
							<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-white/20 text-white backdrop-blur-sm">
								{#if plan.entity_type === 'business_unit'}🏢
								{:else if plan.entity_type === 'division'}🔷
								{:else if plan.entity_type === 'function'}⚙️
								{:else if plan.entity_type === 'section'}📑
								{:else if plan.entity_type === 'unit'}📦
								{:else if plan.entity_type === 'process'}🔄
								{:else if plan.entity_type === 'system'}💻
								{:else if plan.entity_type === 'vendor'}🤝
								{:else if plan.entity_type === 'compliance_domain'}📋
								{:else}📄
								{/if}
								{plan.entity_type.replace('_', ' ')}
							</span>
							<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-white/20 text-white backdrop-blur-sm">
								⏱️ {getDuration()}
							</span>
						</div>
					</div>
					<div class="flex gap-3 ml-6">
						<button
							onclick={openEditModal}
							class="inline-flex items-center gap-2 px-6 py-3 border-2 border-white/30 text-sm font-semibold rounded-xl shadow-lg text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
							</svg>
							Edit
						</button>
						<button
							onclick={handleDelete}
							class="inline-flex items-center gap-2 px-6 py-3 border-2 border-error-200 text-sm font-semibold rounded-xl shadow-lg text-white bg-error-600 hover:bg-error-700 transition-all"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
							</svg>
							Delete
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}

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
				<span class="text-surface-600 dark:text-surface-400 font-medium">Loading audit plan...</span>
			</div>
		</div>
	{:else if plan}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Main Content -->
			<div class="lg:col-span-2 space-y-6">
				<!-- Description -->
				{#if plan.description}
					<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
						<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700 flex items-center gap-2">
							<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
							</svg>
							<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50">Description</h2>
						</div>
						<div class="p-6">
							<p class="text-surface-700 dark:text-surface-300 whitespace-pre-wrap leading-relaxed">{plan.description}</p>
						</div>
					</div>
				{/if}

				<!-- Objectives -->
				{#if plan.objectives}
					<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
						<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700 flex items-center gap-2">
							<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
							</svg>
							<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50">Objectives</h2>
						</div>
						<div class="p-6">
							<p class="text-surface-700 dark:text-surface-300 whitespace-pre-wrap leading-relaxed">{plan.objectives}</p>
						</div>
					</div>
				{/if}

				<!-- Scope -->
				{#if plan.scope}
					<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
						<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700 flex items-center gap-2">
							<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
							<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50">Scope</h2>
						</div>
						<div class="p-6">
							<p class="text-surface-700 dark:text-surface-300 whitespace-pre-wrap leading-relaxed">{plan.scope}</p>
						</div>
					</div>
				{/if}
			</div>

			<!-- Sidebar -->
			<div class="space-y-6">
				<!-- Entity Information -->
				<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
					<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700 flex items-center gap-2">
						<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
						</svg>
						<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50">Entity Information</h2>
					</div>
					<div class="p-6 space-y-4">
						<div class="flex items-start gap-3 p-3 bg-surface-50 dark:bg-surface-900/50 rounded-lg">
							<svg class="w-5 h-5 text-surface-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
							</svg>
							<div class="flex-1">
								<div class="text-xs font-medium text-surface-500 dark:text-surface-400">Entity Name</div>
								<p class="text-sm font-semibold text-surface-900 dark:text-surface-50 mt-1">{plan.entity_name}</p>
							</div>
						</div>
						<div class="flex items-start gap-3 p-3 bg-surface-50 dark:bg-surface-900/50 rounded-lg">
							<svg class="w-5 h-5 text-surface-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
							</svg>
							<div class="flex-1">
								<div class="text-xs font-medium text-surface-500 dark:text-surface-400">Entity Type</div>
								<div class="mt-1">
									<span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold {getEntityTypeColor(plan.entity_type)}">
										{#if plan.entity_type === 'business_unit'}🏢
										{:else if plan.entity_type === 'division'}🔷
										{:else if plan.entity_type === 'function'}⚙️
										{:else if plan.entity_type === 'section'}📑
										{:else if plan.entity_type === 'unit'}📦
										{:else if plan.entity_type === 'process'}🔄
										{:else if plan.entity_type === 'system'}💻
										{:else if plan.entity_type === 'vendor'}🤝
										{:else if plan.entity_type === 'compliance_domain'}📋
										{:else}📄
										{/if}
										{plan.entity_type.replace('_', ' ')}
									</span>
								</div>
							</div>
						</div>
						<div class="flex items-start gap-3 p-3 bg-surface-50 dark:bg-surface-900/50 rounded-lg">
							<svg class="w-5 h-5 text-surface-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
							</svg>
							<div class="flex-1">
								<div class="text-xs font-medium text-surface-500 dark:text-surface-400">Entity ID</div>
								<p class="text-sm font-semibold text-surface-900 dark:text-surface-50 mt-1">#{plan.entity}</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Timeline -->
				<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
					<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700 flex items-center gap-2">
						<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
						</svg>
						<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50">Timeline</h2>
					</div>
					<div class="p-6 space-y-4">
						<div class="flex items-start gap-3 p-3 bg-surface-50 dark:bg-surface-900/50 rounded-lg">
							<svg class="w-5 h-5 text-green-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							<div class="flex-1">
								<div class="text-xs font-medium text-surface-500 dark:text-surface-400">Planned Start</div>
								<p class="text-sm font-semibold text-surface-900 dark:text-surface-50 mt-1">{formatDate(plan.planned_start)}</p>
							</div>
						</div>
						<div class="flex items-start gap-3 p-3 bg-surface-50 dark:bg-surface-900/50 rounded-lg">
							<svg class="w-5 h-5 text-error-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							<div class="flex-1">
								<div class="text-xs font-medium text-surface-500 dark:text-surface-400">Planned End</div>
								<p class="text-sm font-semibold text-surface-900 dark:text-surface-50 mt-1">{formatDate(plan.planned_end)}</p>
							</div>
						</div>
						<div class="flex items-start gap-3 p-3 bg-surface-50 dark:bg-surface-900/50 rounded-lg">
							<svg class="w-5 h-5 text-primary-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
							</svg>
							<div class="flex-1">
								<div class="text-xs font-medium text-surface-500 dark:text-surface-400">Duration</div>
								<p class="text-sm font-semibold text-surface-900 dark:text-surface-50 mt-1">{getDuration()}</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Team -->
				<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
					<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700 flex items-center gap-2">
						<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
						</svg>
						<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50">Team</h2>
					</div>
					<div class="p-6">
						<div class="flex items-start gap-3 p-3 bg-surface-50 dark:bg-surface-900/50 rounded-lg">
							<svg class="w-5 h-5 text-surface-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
							<div class="flex-1">
								<div class="text-xs font-medium text-surface-500 dark:text-surface-400">Lead Auditor</div>
								<p class="text-sm font-semibold text-surface-900 dark:text-surface-50 mt-1">{plan.lead_auditor_display || 'Not assigned'}</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Metadata -->
				<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
					<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700 flex items-center gap-2">
						<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50">Metadata</h2>
					</div>
					<div class="p-6 space-y-4">
						<div class="flex items-start gap-3 p-3 bg-surface-50 dark:bg-surface-900/50 rounded-lg">
							<svg class="w-5 h-5 text-surface-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
							</svg>
							<div class="flex-1">
								<div class="text-xs font-medium text-surface-500 dark:text-surface-400">Created</div>
								<p class="text-sm font-semibold text-surface-900 dark:text-surface-50 mt-1">{formatDateTime(plan.created_at)}</p>
							</div>
						</div>
						<div class="flex items-start gap-3 p-3 bg-surface-50 dark:bg-surface-900/50 rounded-lg">
							<svg class="w-5 h-5 text-surface-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
							</svg>
							<div class="flex-1">
								<div class="text-xs font-medium text-surface-500 dark:text-surface-400">Last Updated</div>
								<p class="text-sm font-semibold text-surface-900 dark:text-surface-50 mt-1">{formatDateTime(plan.updated_at)}</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<!-- Edit Modal -->
{#if showEditModal && plan}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
		<div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
			<div class="p-6">
				<div class="flex justify-between items-center mb-4">
					<h3 class="text-lg font-medium text-surface-900">Edit Audit Plan</h3>
					<button
						onclick={closeEditModal}
						class="text-surface-400 hover:text-surface-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-full p-1"
						aria-label="Close edit modal"
					>
						<i class="fa-solid fa-xmark h-6 w-6"></i>
					</button>
				</div>

				<form onsubmit={(e) => { e.preventDefault(); savePlan(); }} class="space-y-6">
					<!-- Basic Information -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<!-- Title -->
						<div class="md:col-span-2">
							<label for="edit-title" class="block text-sm font-medium text-surface-700 mb-1">Title</label>
							<input
								id="edit-title"
								type="text"
								bind:value={editForm.title}
								required
								class="w-full px-3 py-2 border border-surface-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
							/>
						</div>

						<!-- Planned Start -->
						<div>
							<label for="edit-planned-start" class="block text-sm font-medium text-surface-700 mb-1">Planned Start Date</label>
							<input
								id="edit-planned-start"
								type="date"
								bind:value={editForm.planned_start}
								required
								class="w-full px-3 py-2 border border-surface-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
							/>
						</div>

						<!-- Planned End -->
						<div>
							<label for="edit-planned-end" class="block text-sm font-medium text-surface-700 mb-1">Planned End Date</label>
							<input
								id="edit-planned-end"
								type="date"
								bind:value={editForm.planned_end}
								required
								class="w-full px-3 py-2 border border-surface-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
							/>
						</div>

						<!-- Status -->
						<div>
							<label for="edit-status" class="block text-sm font-medium text-surface-700 mb-1">Status</label>
							<select
								id="edit-status"
								bind:value={editForm.status}
								class="w-full px-3 py-2 border border-surface-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
							>
								{#each statusChoices as choice}
									<option value={choice.value}>{choice.label}</option>
								{/each}
							</select>
						</div>
					</div>

					<!-- Description -->
					<div>
						<label for="edit-description" class="block text-sm font-medium text-surface-700 mb-1">Description</label>
						<textarea
							id="edit-description"
							bind:value={editForm.description}
							rows="3"
							class="w-full px-3 py-2 border border-surface-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
						></textarea>
					</div>

					<!-- Objectives -->
					<div>
						<label for="edit-objectives" class="block text-sm font-medium text-surface-700 mb-1">Objectives</label>
						<textarea
							id="edit-objectives"
							bind:value={editForm.objectives}
							rows="4"
							class="w-full px-3 py-2 border border-surface-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
						></textarea>
					</div>

					<!-- Scope -->
					<div>
						<label for="edit-scope" class="block text-sm font-medium text-surface-700 mb-1">Scope</label>
						<textarea
							id="edit-scope"
							bind:value={editForm.scope}
							rows="4"
							class="w-full px-3 py-2 border border-surface-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
						></textarea>
					</div>

					<!-- Actions -->
					<div class="flex justify-end space-x-3 pt-4">
						<button
							type="button"
							onclick={closeEditModal}
							class="px-4 py-2 border border-surface-300 rounded-md shadow-sm text-sm font-medium text-surface-700 bg-surface-50 hover:bg-surface-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
						>
							Cancel
						</button>
						<button
							type="submit"
							disabled={editing}
							class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
						>
							{#if editing}
								<i class="fa-solid fa-spinner h-4 w-4 mr-2 animate-spin"></i>
								Saving...
							{:else}
								<i class="fa-solid fa-save h-4 w-4 mr-2"></i>
								Save Changes
							{/if}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}
