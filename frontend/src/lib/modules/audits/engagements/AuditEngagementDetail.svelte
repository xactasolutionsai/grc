<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { 
		getEngagement, 
		startEngagement, 
		submitResults, 
		closeEngagement,
		updateProgress,
		deleteEngagement,
		getEngagementTimeline,
		STATUS_COLORS,
		PRIORITY_COLORS,
		canStartEngagement,
		canSubmitResults,
		canCloseEngagement,
		isEngagementOverdue,
		formatEngagementStatus,
		formatEngagementPriority
	} from './api.js';
	import { listExecutions, createExecution } from '$lib/modules/audits/checklists/execution-api.js';
	import { listChecklists } from '$lib/modules/audits/checklists/api.js';
	import EnhancedModal from '$lib/components/Modals/EnhancedModal.svelte';

	export let engagementId;
	export let onEdit = () => {};
	export let onClose = () => {};

	function handleEdit(engagement) {
		goto(`/audits/engagements/${engagement.id}/edit`);
	}

	function handleClose() {
		goto('/audits/engagements');
	}

	let engagement = null;
	let timeline = null;
	let loading = true;
	let error = null;
	let actionLoading = false;
	let showSubmitModal = false;
	let showCloseModal = false;
	let showProgressModal = false;
	let showTimeline = false;
	let showDeleteModal = false;
	let deleting = false;

	// Checklist execution state
	let executions = [];
	let availableChecklists = [];
	let showExecutionModal = false;
	let selectedChecklist = null;
	let executionsLoading = false;

	// Actual cost editing
	let editingActualCost = false;
	let actualCostValue = '';

	// Modal form data
	let submitData = {
		findings_summary: '',
		recommendations: ''
	};
	let closeData = {
		closure_notes: ''
	};
	let progressData = {
		progress_percentage: 0,
		fieldwork_notes: ''
	};

	onMount(async () => {
		await loadEngagement();
		await loadTimeline();
		await loadExecutions();
	});

	async function loadEngagement() {
		loading = true;
		try {
			engagement = await getEngagement(engagementId);
		} catch (err) {
			console.error('Error loading engagement:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	}

	async function loadTimeline() {
		try {
			timeline = await getEngagementTimeline(engagementId);
		} catch (err) {
			console.error('Error loading timeline:', err);
		}
	}

	async function loadExecutions() {
		executionsLoading = true;
		try {
			const data = await listExecutions({ audit_engagement: engagementId });
			executions = data.results || data;
		} catch (err) {
			console.error('Error loading executions:', err);
		} finally {
			executionsLoading = false;
		}
	}

	async function loadAvailableChecklists() {
		try {
			const data = await listChecklists({ status: 'active' });
			availableChecklists = data.results || data;
		} catch (err) {
			console.error('Error loading checklists:', err);
		}
	}

	async function openExecutionModal() {
		await loadAvailableChecklists();
		selectedChecklist = null;
		showExecutionModal = true;
	}

	async function handleCreateExecution() {
		if (!selectedChecklist) {
			error = 'Please select a checklist';
			return;
		}

		try {
			await createExecution({
				checklist: selectedChecklist,
				audit_engagement: engagementId,
				status: 'in_progress'
			});
			showExecutionModal = false;
			await loadExecutions();
		} catch (err) {
			console.error('Error creating execution:', err);
			error = err.message;
		}
	}

	function openExecution(executionId) {
		goto(`/audits/executions/${executionId}`);
	}

	// Actual cost editing functions
	function startEditActualCost() {
		editingActualCost = true;
		actualCostValue = engagement.actual_cost || '';
	}

	function cancelEditActualCost() {
		editingActualCost = false;
		actualCostValue = '';
	}

	async function saveActualCost() {
		try {
			// Update the engagement with the new actual cost
			const response = await fetch(`/fe-api/audits/engagements/${engagementId}`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					actual_cost: actualCostValue ? parseFloat(actualCostValue) : null
				})
			});

			if (response.ok) {
				// Update the local engagement object
				engagement.actual_cost = actualCostValue ? parseFloat(actualCostValue) : null;
				editingActualCost = false;
				actualCostValue = '';
			} else {
				console.error('Failed to update actual cost');
			}
		} catch (err) {
			console.error('Error updating actual cost:', err);
		}
	}

	async function handleAction(action) {
		actionLoading = true;
		try {
			switch (action) {
				case 'start':
					await startEngagement(engagementId);
					break;
				case 'submit':
					await submitResults(engagementId, submitData);
					showSubmitModal = false;
					submitData = { findings_summary: '', recommendations: '' };
					break;
				case 'close':
					await closeEngagement(engagementId, closeData);
					showCloseModal = false;
					closeData = { closure_notes: '' };
					break;
				case 'progress':
					await updateProgress(engagementId, progressData);
					showProgressModal = false;
					break;
			}
			await loadEngagement();
			await loadTimeline();
		} catch (err) {
			console.error(`Error ${action}ing engagement:`, err);
			error = err.message;
		} finally {
			actionLoading = false;
		}
	}

	function formatDate(dateString) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleDateString();
	}

	function formatDateTime(dateString) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleString();
	}

	async function handleDelete() {
		deleting = true;
		try {
			await deleteEngagement(engagementId);
			goto('/audits/engagements');
		} catch (err) {
			console.error('Error deleting engagement:', err);
			error = err.message;
		} finally {
			deleting = false;
		}
	}

	function confirmDelete() {
		showDeleteModal = true;
	}

	function cancelDelete() {
		showDeleteModal = false;
	}

	function getEventColor(color, status) {
		const colorMap = {
			blue: status === 'completed' ? 'bg-blue-500' : 'bg-blue-100',
			green: status === 'completed' ? 'bg-green-500' : 'bg-green-100',
			yellow: status === 'completed' ? 'bg-yellow-500' : 'bg-yellow-100',
			purple: status === 'completed' ? 'bg-purple-500' : 'bg-purple-100',
			gray: status === 'completed' ? 'bg-gray-500' : 'bg-gray-100',
			red: status === 'warning' ? 'bg-red-500' : 'bg-red-100'
		};
		return colorMap[color] || 'bg-gray-500';
	}

	function getEventIcon(icon) {
		const iconMap = {
			'plus-circle': '<svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd"></path></svg>',
			'play-circle': '<svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"></path></svg>',
			'search': '<svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"></path></svg>',
			'eye': '<svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20"><path d="M10 12a2 2 0 100-4 2 2 0 000 4z"></path><path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"></path></svg>',
			'check-circle': '<svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>',
			'lock-closed': '<svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"></path></svg>',
			'exclamation-triangle': '<svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>'
		};
		return iconMap[icon] || '<svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>';
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
</script>

<div class="mx-auto p-6">
	{#if loading}
		<div class="flex justify-center items-center py-16">
			<div class="flex flex-col items-center gap-4">
				<svg class="animate-spin h-12 w-12 text-primary-600" fill="none" viewBox="0 0 24 24">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
				</svg>
				<span class="text-surface-600 dark:text-surface-400 font-medium">Loading engagement...</span>
			</div>
		</div>
	{:else if error}
		<div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-4 mb-6 shadow-sm flex items-start gap-3">
			<svg class="h-5 w-5 text-error-600 dark:text-error-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<div class="text-error-800 dark:text-error-200">Error: {error}</div>
		</div>
	{:else if engagement}
		<!-- Header Card -->
		<div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 shadow-xl rounded-xl mb-8 overflow-hidden">
			<div class="p-8">
				<div class="flex justify-between items-start">
					<div class="flex-1">
						<div class="flex items-center gap-3 mb-3">
							<div class="p-3 bg-white/10 rounded-xl">
								<svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								</svg>
							</div>
							<div>
								<h1 class="text-3xl font-bold text-white">{engagement.title}</h1>
								{#if engagement.description}
									<p class="text-primary-100 mt-1">{engagement.description}</p>
								{/if}
							</div>
						</div>
						<div class="flex items-center gap-3 mt-4 flex-wrap">
							<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-white/20 text-white backdrop-blur-sm whitespace-nowrap">
								{formatEngagementStatus(engagement.status)}
							</span>
							<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-white/20 text-white backdrop-blur-sm whitespace-nowrap">
								{formatEngagementPriority(engagement.priority)}
							</span>
							<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-white/20 text-white backdrop-blur-sm">
								📈 {engagement.progress_percentage}% Complete
							</span>
							{#if isEngagementOverdue(engagement)}
								<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-error-600 text-white">
									⚠️ OVERDUE
								</span>
							{/if}
						</div>
					</div>
					<div class="flex gap-3 ml-6">
						<button
							on:click={() => handleEdit(engagement)}
							class="inline-flex items-center gap-2 px-6 py-3 border-2 border-white/30 text-sm font-semibold rounded-xl shadow-lg text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
							</svg>
							Edit
						</button>
						<button
							on:click={confirmDelete}
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

		<!-- Progress Bar Card -->
		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6 mb-6">
			<div class="flex justify-between items-center mb-3">
				<span class="text-sm font-semibold text-surface-900 dark:text-surface-50">Overall Progress</span>
				<span class="text-sm font-bold text-primary-600 dark:text-primary-400">{engagement.progress_percentage}%</span>
			</div>
			<div class="w-full bg-surface-200 dark:bg-surface-700 rounded-full h-3">
				<div 
					class="h-3 rounded-full {getProgressColor(engagement.progress_percentage)} transition-all duration-300"
					style="width: {engagement.progress_percentage}%"
				></div>
			</div>
		</div>

		<!-- Action Buttons -->
		<div class="flex flex-wrap gap-3 mb-8">
			{#if canStartEngagement(engagement)}
				<button
					on:click={() => handleAction('start')}
					disabled={actionLoading}
					class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-xl font-semibold shadow-lg transition-all"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					Start Engagement
				</button>
			{/if}
			{#if canSubmitResults(engagement)}
				<button
					on:click={() => showSubmitModal = true}
					disabled={actionLoading}
					class="inline-flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded-xl font-semibold shadow-lg transition-all"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					Submit Results
				</button>
			{/if}
			{#if canCloseEngagement(engagement)}
				<button
					on:click={() => showCloseModal = true}
					disabled={actionLoading}
					class="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-xl font-semibold shadow-lg transition-all"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					Close Engagement
				</button>
			{/if}
			<button
				on:click={() => showProgressModal = true}
				disabled={actionLoading}
				class="inline-flex items-center gap-2 px-6 py-3 bg-yellow-600 hover:bg-yellow-700 disabled:opacity-50 text-white rounded-xl font-semibold shadow-lg transition-all"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
				</svg>
				Update Progress
			</button>
			<button
				on:click={() => showTimeline = !showTimeline}
				class="inline-flex items-center gap-2 px-6 py-3 border-2 border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-50 bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 rounded-xl font-semibold shadow-lg transition-all"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				{showTimeline ? 'Hide' : 'Show'} Timeline
			</button>
		</div>

		<!-- Main Content -->
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Left Column -->
			<div class="lg:col-span-2 space-y-6">
				<!-- Timeline -->
				{#if showTimeline && timeline}
					<div class="bg-white shadow rounded-lg p-6">
						<div class="flex items-center justify-between mb-6">
							<h3 class="text-lg font-medium text-gray-900">Engagement Timeline</h3>
							<div class="flex items-center space-x-2">
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {timeline.is_overdue ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}">
									{timeline.current_status.replace('_', ' ').toUpperCase()}
								</span>
								<span class="text-sm text-gray-500">{timeline.progress_percentage}% Complete</span>
							</div>
						</div>
						
						<div class="flow-root">
							<ul class="-mb-8">
								{#each timeline.events as event, index}
									<li>
										<div class="relative pb-8">
											{#if index < timeline.events.length - 1}
												<span class="absolute top-4 left-4 -ml-px h-full w-0.5 {event.status === 'warning' ? 'bg-red-200' : 'bg-gray-200'}" aria-hidden="true"></span>
											{/if}
											<div class="relative flex space-x-3">
												<div>
													<span class="h-8 w-8 rounded-full {getEventColor(event.color, event.status)} flex items-center justify-center ring-8 ring-white">
														{@html getEventIcon(event.icon)}
													</span>
												</div>
												<div class="min-w-0 flex-1 pt-1.5">
													<div class="flex items-center justify-between">
														<div class="flex-1">
															<p class="text-sm font-medium text-gray-900">{event.action}</p>
															<p class="text-sm text-gray-600 mt-1">{event.description}</p>
															{#if event.user}
																<p class="text-xs text-gray-500 mt-1">by {event.user}</p>
															{/if}
														</div>
														<div class="text-right text-sm whitespace-nowrap text-gray-500 ml-4">
															{formatDateTime(event.date)}
														</div>
													</div>
													{#if event.status === 'in_progress'}
														<div class="mt-2">
															<div class="w-full bg-gray-200 rounded-full h-2">
																<div class="bg-blue-600 h-2 rounded-full" style="width: {timeline.progress_percentage}%"></div>
															</div>
															<p class="text-xs text-gray-500 mt-1">In Progress</p>
														</div>
													{/if}
													{#if event.status === 'warning'}
														<div class="mt-2 p-2 bg-red-50 border border-red-200 rounded-md">
															<p class="text-xs text-red-800 font-medium">⚠️ {event.description}</p>
														</div>
													{/if}
												</div>
											</div>
										</div>
									</li>
								{/each}
							</ul>
						</div>
					</div>
				{/if}

				<!-- Basic Information -->
				<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
					<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
						<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
							<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Basic Information
						</h3>
					</div>
					<div class="p-6">
						<dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">📑 Audit Plan</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">
									<a href="/audits/planning/{engagement.audit_plan}" class="text-primary-600 hover:text-primary-800 dark:hover:text-primary-400">
										{engagement.audit_plan_title || '—'}
									</a>
								</dd>
							</div>
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">🏢 Entity</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">
									<a href="/audits/universe/{engagement.entity}" class="text-primary-600 hover:text-primary-800 dark:hover:text-primary-400">
										{engagement.entity_name || '—'}
									</a>
								</dd>
							</div>
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">👤 Assigned Auditor</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">{engagement.assigned_auditor_display || '—'}</dd>
							</div>
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">👔 Engagement Lead</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">{engagement.engagement_lead_display || '—'}</dd>
							</div>
						</dl>
					</div>
				</div>

				<!-- Schedule -->
				<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
					<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
						<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
							<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
							</svg>
							Schedule
						</h3>
					</div>
					<div class="p-6">
						<dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">📅 Planned Start Date</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">{formatDate(engagement.planned_start_date)}</dd>
							</div>
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">📅 Planned End Date</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">{formatDate(engagement.planned_end_date)}</dd>
							</div>
							{#if engagement.actual_start_date}
								<div>
									<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">✅ Actual Start Date</dt>
									<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">{formatDate(engagement.actual_start_date)}</dd>
								</div>
							{/if}
							{#if engagement.actual_end_date}
								<div>
									<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">✅ Actual End Date</dt>
									<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">{formatDate(engagement.actual_end_date)}</dd>
								</div>
							{/if}
						</dl>
					</div>
				</div>

				<!-- Scope and Objectives -->
				{#if engagement.scope || engagement.objectives || engagement.methodology}
					<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
						<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
							<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
								<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
								</svg>
								Scope & Objectives
							</h3>
						</div>
						<div class="p-6 space-y-6">
							{#if engagement.scope}
								<div>
									<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">🎯 Scope</dt>
									<dd class="text-sm text-surface-900 dark:text-surface-50 whitespace-pre-wrap bg-surface-50 dark:bg-surface-900/50 p-4 rounded-lg border border-surface-200 dark:border-surface-700">{engagement.scope}</dd>
								</div>
							{/if}
							{#if engagement.objectives}
								<div>
									<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">🎯 Objectives</dt>
									<dd class="text-sm text-surface-900 dark:text-surface-50 whitespace-pre-wrap bg-surface-50 dark:bg-surface-900/50 p-4 rounded-lg border border-surface-200 dark:border-surface-700">{engagement.objectives}</dd>
								</div>
							{/if}
							{#if engagement.methodology}
								<div>
									<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">⚙️ Methodology</dt>
									<dd class="text-sm text-surface-900 dark:text-surface-50 whitespace-pre-wrap bg-surface-50 dark:bg-surface-900/50 p-4 rounded-lg border border-surface-200 dark:border-surface-700">{engagement.methodology}</dd>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Results -->
				{#if engagement.findings_summary || engagement.recommendations}
					<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
						<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
							<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
								<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								Results
							</h3>
						</div>
						<div class="p-6 space-y-6">
							{#if engagement.findings_summary}
								<div>
									<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">🔍 Findings Summary</dt>
									<dd class="text-sm text-surface-900 dark:text-surface-50 whitespace-pre-wrap bg-surface-50 dark:bg-surface-900/50 p-4 rounded-lg border border-surface-200 dark:border-surface-700">{engagement.findings_summary}</dd>
								</div>
							{/if}
							{#if engagement.recommendations}
								<div>
									<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">💡 Recommendations</dt>
									<dd class="text-sm text-surface-900 dark:text-surface-50 whitespace-pre-wrap bg-surface-50 dark:bg-surface-900/50 p-4 rounded-lg border border-surface-200 dark:border-surface-700">{engagement.recommendations}</dd>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Checklist Executions -->
				<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
					<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700 flex items-center justify-between">
						<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
							<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
							</svg>
							Checklist Executions
						</h3>
						<button
							on:click={openExecutionModal}
							class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold rounded-lg transition-colors shadow-sm"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							Execute Checklist
						</button>
					</div>
					<div class="p-6">
						{#if executionsLoading}
							<div class="flex justify-center py-8">
								<svg class="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
							</div>
						{:else if executions.length === 0}
							<div class="text-center py-8">
								<svg class="mx-auto h-12 w-12 text-surface-400 dark:text-surface-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
								</svg>
								<p class="text-surface-600 dark:text-surface-400 text-sm">No checklist executions yet</p>
								<p class="text-surface-500 dark:text-surface-500 text-xs mt-1">Click "Execute Checklist" to start testing</p>
							</div>
						{:else}
							<div class="grid gap-4 md:grid-cols-2">
								{#each executions as execution}
									<div
										class="border-2 border-surface-200 dark:border-surface-700 rounded-lg p-4 cursor-pointer hover:border-primary-500 dark:hover:border-primary-400 hover:bg-surface-50 dark:hover:bg-surface-700/50 transition-all group"
										on:click={() => openExecution(execution.id)}
										on:keydown={(e) => e.key === 'Enter' && openExecution(execution.id)}
										role="button"
										tabindex="0"
									>
										<div class="flex items-start justify-between mb-3">
											<h4 class="text-sm font-semibold text-surface-900 dark:text-surface-50 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
												{execution.checklist_name}
											</h4>
											<span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium
												{execution.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
												execution.status === 'in_progress' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' :
												'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400'}">
												{execution.status === 'completed' ? '✓ Complete' :
												execution.status === 'in_progress' ? '⏳ In Progress' :
												'⚪ Not Started'}
											</span>
										</div>
										
										<!-- Progress Bar -->
										<div class="mb-2">
											<div class="flex justify-between text-xs text-surface-600 dark:text-surface-400 mb-1">
												<span>{execution.completed_items} / {execution.total_items} items</span>
												<span>{execution.progress_percentage}%</span>
											</div>
											<div class="w-full bg-surface-200 dark:bg-surface-700 rounded-full h-2 overflow-hidden">
												<div 
													class="bg-primary-600 h-2 transition-all duration-300 rounded-full"
													style="width: {execution.progress_percentage}%"
												></div>
											</div>
										</div>

										<!-- Metadata -->
										<div class="flex items-center gap-4 text-xs text-surface-500 dark:text-surface-500 mt-3">
											{#if execution.started_by_display}
												<span class="flex items-center gap-1">
													<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
													</svg>
													{execution.started_by_display}
												</span>
											{/if}
											{#if execution.started_at}
												<span class="flex items-center gap-1">
													<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
													</svg>
													{new Date(execution.started_at).toLocaleDateString()}
												</span>
											{/if}
										</div>
									</div>
								{/each}
							</div>
						{/if}
					</div>
				</div>

				
			</div>

			<!-- Right Column -->
			<div class="space-y-6">
				<!-- Resources -->
				<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
					<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
						<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
							<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Resources
						</h3>
					</div>
					<div class="p-6">
						<dl class="space-y-5">
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">⏱️ Estimated Hours</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">{engagement.estimated_hours || '—'}</dd>
							</div>
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">⏰ Actual Hours</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">{engagement.actual_hours || '—'}</dd>
							</div>
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">💵 Budget Allocated</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">{engagement.budget_allocated ? `$${engagement.budget_allocated}` : '—'}</dd>
							</div>
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">💰 Actual Cost</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">
									{#if editingActualCost}
										<div class="flex flex-col gap-2 mt-2">
											<input
												type="number"
												step="0.01"
												min="0"
												bind:value={actualCostValue}
												class="w-full px-3 py-2 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
												placeholder="0.00"
											/>
											<div class="flex gap-2">
												<button
													on:click={saveActualCost}
													class="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white text-xs font-semibold rounded-lg transition-colors"
												>
													Save
												</button>
												<button
													on:click={cancelEditActualCost}
													class="flex-1 px-3 py-2 bg-surface-200 dark:bg-surface-700 hover:bg-surface-300 dark:hover:bg-surface-600 text-surface-900 dark:text-surface-50 text-xs font-semibold rounded-lg transition-colors"
												>
													Cancel
												</button>
											</div>
										</div>
									{:else}
										<div class="flex items-center justify-between">
											<span>{engagement.actual_cost ? `$${engagement.actual_cost}` : '—'}</span>
											<button
												on:click={startEditActualCost}
												class="text-primary-600 hover:text-primary-800 dark:hover:text-primary-400 text-xs font-semibold"
											>
												Edit
											</button>
										</div>
									{/if}
								</dd>
							</div>
						</dl>
					</div>
				</div>

				<!-- Additional Information -->
				<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
					<div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
						<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
							<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Metadata
						</h3>
					</div>
					<div class="p-6">
						<dl class="space-y-5">
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">📅 Created</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">
									{formatDateTime(engagement.created_at)}
									{#if engagement.created_by_display}
										<div class="text-xs text-surface-500 dark:text-surface-400 mt-1">by {engagement.created_by_display}</div>
									{/if}
								</dd>
							</div>
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">🔄 Last Updated</dt>
								<dd class="text-sm font-semibold text-surface-900 dark:text-surface-50">{formatDateTime(engagement.updated_at)}</dd>
							</div>
							{#if engagement.tags && engagement.tags.length > 0}
								<div>
									<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">🏷️ Tags</dt>
									<dd class="mt-2">
										<div class="flex flex-wrap gap-2">
											{#each engagement.tags as tag}
												<span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold bg-surface-100 dark:bg-surface-700 text-surface-900 dark:text-surface-50">
													{tag}
												</span>
											{/each}
										</div>
									</dd>
								</div>
							{/if}
							<div>
								<dt class="text-xs font-medium text-surface-500 dark:text-surface-400 mb-2">✅ Status</dt>
								<dd class="mt-2">
									<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold {engagement.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400' : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'}">
										{engagement.is_active ? 'Active' : 'Inactive'}
									</span>
								</dd>
							</div>
						</dl>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<!-- Submit Results Modal -->
{#if showSubmitModal}
	<div class="fixed inset-0 bg-surface-900/50 dark:bg-black/70 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
		<div class="bg-white dark:bg-surface-800 rounded-xl shadow-2xl border border-surface-200 dark:border-surface-700 w-full max-w-lg">
			<div class="px-6 py-4 bg-gradient-to-r from-green-600 to-green-700 rounded-t-xl">
				<h3 class="text-xl font-bold text-white flex items-center gap-2">
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					Submit Results
				</h3>
			</div>
			<div class="p-6 space-y-4">
				<div>
					<label for="findings_summary" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">🔍 Findings Summary</label>
					<textarea
						id="findings_summary"
						bind:value={submitData.findings_summary}
						rows="4"
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none"
						placeholder="Enter findings summary..."
					></textarea>
				</div>
				<div>
					<label for="recommendations" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">💡 Recommendations</label>
					<textarea
						id="recommendations"
						bind:value={submitData.recommendations}
						rows="4"
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none"
						placeholder="Enter recommendations..."
					></textarea>
				</div>
			</div>
			<div class="px-6 py-4 bg-surface-50 dark:bg-surface-900/50 rounded-b-xl flex justify-end gap-3">
				<button
					on:click={() => showSubmitModal = false}
					class="px-6 py-2.5 bg-surface-200 dark:bg-surface-700 hover:bg-surface-300 dark:hover:bg-surface-600 text-surface-900 dark:text-surface-50 font-semibold rounded-xl transition-colors"
				>
					Cancel
				</button>
				<button
					on:click={() => handleAction('submit')}
					disabled={actionLoading}
					class="px-6 py-2.5 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-semibold rounded-xl transition-colors"
				>
					{actionLoading ? 'Submitting...' : 'Submit Results'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Close Engagement Modal -->
{#if showCloseModal}
	<div class="fixed inset-0 bg-surface-900/50 dark:bg-black/70 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
		<div class="bg-white dark:bg-surface-800 rounded-xl shadow-2xl border border-surface-200 dark:border-surface-700 w-full max-w-lg">
			<div class="px-6 py-4 bg-gradient-to-r from-purple-600 to-purple-700 rounded-t-xl">
				<h3 class="text-xl font-bold text-white flex items-center gap-2">
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					Close Engagement
				</h3>
			</div>
			<div class="p-6">
				<label for="closure_notes" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">📝 Closure Notes</label>
				<textarea
					id="closure_notes"
					bind:value={closeData.closure_notes}
					rows="5"
					class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none"
					placeholder="Enter closure notes..."
				></textarea>
			</div>
			<div class="px-6 py-4 bg-surface-50 dark:bg-surface-900/50 rounded-b-xl flex justify-end gap-3">
				<button
					on:click={() => showCloseModal = false}
					class="px-6 py-2.5 bg-surface-200 dark:bg-surface-700 hover:bg-surface-300 dark:hover:bg-surface-600 text-surface-900 dark:text-surface-50 font-semibold rounded-xl transition-colors"
				>
					Cancel
				</button>
				<button
					on:click={() => handleAction('close')}
					disabled={actionLoading}
					class="px-6 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-semibold rounded-xl transition-colors"
				>
					{actionLoading ? 'Closing...' : 'Close Engagement'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Update Progress Modal -->
{#if showProgressModal}
	<div class="fixed inset-0 bg-surface-900/50 dark:bg-black/70 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
		<div class="bg-white dark:bg-surface-800 rounded-xl shadow-2xl border border-surface-200 dark:border-surface-700 w-full max-w-lg">
			<div class="px-6 py-4 bg-gradient-to-r from-yellow-600 to-yellow-700 rounded-t-xl">
				<h3 class="text-xl font-bold text-white flex items-center gap-2">
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
					</svg>
					Update Progress
				</h3>
			</div>
			<div class="p-6 space-y-4">
				<div>
					<label for="progress_percentage" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">📈 Progress Percentage</label>
					<input
						id="progress_percentage"
						type="number"
						min="0"
						max="100"
						bind:value={progressData.progress_percentage}
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
						placeholder="Enter percentage (0-100)"
					/>
				</div>
				<div>
					<label for="fieldwork_notes" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">📝 Fieldwork Notes</label>
					<textarea
						id="fieldwork_notes"
						bind:value={progressData.fieldwork_notes}
						rows="4"
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 resize-none"
						placeholder="Enter fieldwork notes..."
					></textarea>
				</div>
			</div>
			<div class="px-6 py-4 bg-surface-50 dark:bg-surface-900/50 rounded-b-xl flex justify-end gap-3">
				<button
					on:click={() => showProgressModal = false}
					class="px-6 py-2.5 bg-surface-200 dark:bg-surface-700 hover:bg-surface-300 dark:hover:bg-surface-600 text-surface-900 dark:text-surface-50 font-semibold rounded-xl transition-colors"
				>
					Cancel
				</button>
				<button
					on:click={() => handleAction('progress')}
					disabled={actionLoading}
					class="px-6 py-2.5 bg-yellow-600 hover:bg-yellow-700 disabled:opacity-50 text-white font-semibold rounded-xl transition-colors"
				>
					{actionLoading ? 'Updating...' : 'Update Progress'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal}
	<div class="fixed inset-0 bg-surface-900/50 dark:bg-black/70 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
		<div class="bg-white dark:bg-surface-800 rounded-xl shadow-2xl border border-surface-200 dark:border-surface-700 w-full max-w-md">
			<div class="p-6 text-center">
				<div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-error-100 dark:bg-error-900/20 mb-4">
					<svg class="h-8 w-8 text-error-600 dark:text-error-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
					</svg>
				</div>
				<h3 class="text-xl font-bold text-surface-900 dark:text-surface-50 mb-2">Delete Engagement</h3>
				<p class="text-sm text-surface-600 dark:text-surface-400 mb-6">
					Are you sure you want to delete this engagement? This action cannot be undone.
				</p>
				<div class="flex gap-3 justify-center">
					<button
						on:click={cancelDelete}
						disabled={deleting}
						class="px-6 py-2.5 bg-surface-200 dark:bg-surface-700 hover:bg-surface-300 dark:hover:bg-surface-600 text-surface-900 dark:text-surface-50 font-semibold rounded-xl transition-colors disabled:opacity-50"
					>
						Cancel
					</button>
					<button
						on:click={handleDelete}
						disabled={deleting}
						class="px-6 py-2.5 bg-error-600 hover:bg-error-700 text-white font-semibold rounded-xl transition-colors disabled:opacity-50"
					>
						{deleting ? 'Deleting...' : 'Delete'}
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- Execute Checklist Modal -->
<EnhancedModal
	bind:open={showExecutionModal}
	title="Execute Checklist"
	maxWidth="lg"
	onClose={() => showExecutionModal = false}
>
	<div class="space-y-4">
		<p class="text-sm text-surface-600 dark:text-surface-400">
			Select a checklist to execute for this audit engagement
		</p>

		<div>
			<label for="checklist-select" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
				Checklist
			</label>
			<select
				id="checklist-select"
				bind:value={selectedChecklist}
				class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
			>
				<option value={null}>Select a checklist...</option>
				{#each availableChecklists as checklist}
					<option value={checklist.id}>{checklist.name}</option>
				{/each}
			</select>
			{#if availableChecklists.length === 0}
				<p class="mt-2 text-xs text-surface-500 dark:text-surface-400">
					No active checklists available. Create a checklist first.
				</p>
			{/if}
		</div>

		<div class="flex justify-end gap-3 mt-6 pt-4 border-t border-surface-200 dark:border-surface-700">
			<button
				on:click={() => showExecutionModal = false}
				class="px-6 py-2.5 border-2 border-surface-300 dark:border-surface-600 rounded-xl shadow-sm text-sm font-semibold text-surface-700 dark:text-surface-200 bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 transition-all"
			>
				Cancel
			</button>
			<button
				on:click={handleCreateExecution}
				disabled={!selectedChecklist}
				class="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors shadow-sm"
			>
				Start Execution
			</button>
		</div>
	</div>
</EnhancedModal>

