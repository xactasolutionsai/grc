<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getExecution, updateItemResult, completeExecution, startExecution, getExecutionSummary } from './execution-api.js';

	interface Props {
		executionId: number | string;
	}

	let { executionId }: Props = $props();

	interface ItemResult {
		id: number;
		execution: number;
		checklist_item: number;
		checklist_item_title: string;
		checklist_item_description: string;
		checklist_item_order: number;
		result: string;
		comments: string;
		finding_summary: string;
		tested_by: number | null;
		tested_by_display: string | null;
		tested_at: string | null;
		control_name: string | null;
		risk_name: string | null;
		policy_name: string | null;
		evidence_notes: string;
		created_at: string;
		updated_at: string;
	}

	interface Execution {
		id: number;
		checklist: number;
		checklist_name: string;
		audit_engagement: number;
		engagement_title: string;
		status: string;
		started_by: number | null;
		started_by_display: string | null;
		started_at: string | null;
		completed_by: number | null;
		completed_by_display: string | null;
		completed_at: string | null;
		total_items: number;
		completed_items: number;
		progress_percentage: number;
		notes: string;
		item_results: ItemResult[];
		created_at: string;
		updated_at: string;
	}

	interface Summary {
		total: number;
		not_tested: number;
		pass: number;
		fail: number;
		needs_followup: number;
		not_applicable: number;
	}

	let execution = $state<Execution | null>(null);
	let summary = $state<Summary>({ total: 0, not_tested: 0, pass: 0, fail: 0, needs_followup: 0, not_applicable: 0 });
	let loading = $state(true);
	let error = $state<string | null>(null);
	let saving = $state(false);
	let expandedItems = $state<Set<number>>(new Set());

	const RESULT_CHOICES = [
		{ value: 'not_tested', label: 'Not Tested', color: 'gray', icon: '⚪' },
		{ value: 'pass', label: 'Pass', color: 'green', icon: '✅' },
		{ value: 'fail', label: 'Fail', color: 'red', icon: '❌' },
		{ value: 'needs_followup', label: 'Needs Follow-up', color: 'yellow', icon: '⚠️' },
		{ value: 'not_applicable', label: 'Not Applicable', color: 'gray', icon: '➖' }
	];

	onMount(async () => {
		await loadExecution();
	});

	async function loadExecution() {
		loading = true;
		error = null;
		try {
			execution = await getExecution(executionId);
			await loadSummary();
		} catch (err: any) {
			error = err.message;
		} finally {
			loading = false;
		}
	}

	async function loadSummary() {
		try {
			summary = await getExecutionSummary(executionId);
		} catch (err) {
			console.error('Error loading summary:', err);
		}
	}

	async function handleResultChange(itemResult: ItemResult, newResult: string) {
		saving = true;
		try {
			const updated = await updateItemResult(itemResult.id, { result: newResult });
			// Update the item in the execution
			if (execution && execution.item_results) {
				const index = execution.item_results.findIndex(ir => ir.id === itemResult.id);
				if (index !== -1) {
					execution.item_results[index] = { ...execution.item_results[index], ...updated };
				}
			}
			await loadExecution(); // Reload to get updated progress
		} catch (err: any) {
			error = err.message;
		} finally {
			saving = false;
		}
	}

	async function handleCommentSave(itemResult: ItemResult) {
		saving = true;
		try {
			const updated = await updateItemResult(itemResult.id, {
				comments: itemResult.comments,
				finding_summary: itemResult.finding_summary
			});
			// Update the item in the execution
			if (execution && execution.item_results) {
				const index = execution.item_results.findIndex(ir => ir.id === itemResult.id);
				if (index !== -1) {
					execution.item_results[index] = { ...execution.item_results[index], ...updated };
				}
			}
		} catch (err: any) {
			error = err.message;
		} finally {
			saving = false;
		}
	}

	async function handleStartExecution() {
		saving = true;
		try {
			execution = await startExecution(executionId);
		} catch (err: any) {
			error = err.message;
		} finally {
			saving = false;
		}
	}

	async function handleCompleteExecution() {
		saving = true;
		try {
			execution = await completeExecution(executionId);
		} catch (err: any) {
			error = err.message;
		} finally {
			saving = false;
		}
	}

	function toggleExpanded(itemId: number) {
		if (expandedItems.has(itemId)) {
			expandedItems.delete(itemId);
		} else {
			expandedItems.add(itemId);
		}
		expandedItems = new Set(expandedItems);
	}

	function getResultChoice(result: string) {
		return RESULT_CHOICES.find(c => c.value === result) || RESULT_CHOICES[0];
	}

	function getStatusColor(status: string) {
		switch (status) {
			case 'not_started': return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
			case 'in_progress': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
			case 'completed': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
			default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
		}
	}

	function formatDate(dateString: string) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleString();
	}

	function goBackToEngagement() {
		if (execution) {
			goto(`/audits/engagements/${execution.audit_engagement}`);
		}
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
				<span class="text-surface-600 dark:text-surface-400 font-medium">Loading execution...</span>
			</div>
		</div>
	{:else if error}
		<div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-4 mb-6 shadow-sm">
			<div class="text-error-800 dark:text-error-200">Error: {error}</div>
		</div>
	{:else if execution}
		<!-- Breadcrumb Navigation -->
		<nav class="flex items-center gap-2 mb-6 text-sm">
			<button
				onclick={() => goto('/audits/engagements')}
				class="text-surface-600 dark:text-surface-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
			>
				Audit Engagements
			</button>
			<svg class="w-4 h-4 text-surface-400 dark:text-surface-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
			</svg>
			<button
				onclick={goBackToEngagement}
				class="text-surface-600 dark:text-surface-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors font-medium"
			>
				{execution.engagement_title}
			</button>
			<svg class="w-4 h-4 text-surface-400 dark:text-surface-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
			</svg>
			<span class="text-surface-900 dark:text-surface-50 font-semibold">Checklist Execution</span>
		</nav>

		<!-- Back Button -->
		<button
			onclick={goBackToEngagement}
			class="inline-flex items-center gap-2 px-4 py-2 mb-6 text-sm font-medium text-surface-700 dark:text-surface-300 bg-white dark:bg-surface-800 border-2 border-surface-300 dark:border-surface-600 rounded-lg hover:bg-surface-50 dark:hover:bg-surface-700 transition-all shadow-sm"
		>
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
			</svg>
			Back to Engagement
		</button>
		<!-- Header Card -->
		<div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 shadow-xl rounded-xl mb-8 p-8">
			<div class="flex justify-between items-start">
				<div class="flex-1">
					<div class="flex items-center gap-3 mb-4">
						<div class="p-3 bg-white/10 rounded-xl">
							<svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
							</svg>
						</div>
						<div>
							<h1 class="text-3xl font-bold text-white">{execution.checklist_name}</h1>
							<p class="text-primary-100 mt-1">Engagement: {execution.engagement_title}</p>
						</div>
					</div>

					<!-- Status Badge -->
					<span class="inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold {getStatusColor(execution.status)}">
						{execution.status.replace('_', ' ').toUpperCase()}
					</span>

					<!-- Progress Bar -->
					<div class="mt-6">
						<div class="flex justify-between text-white text-sm mb-2">
							<span>Progress</span>
							<span>{execution.completed_items} / {execution.total_items} ({execution.progress_percentage}%)</span>
						</div>
						<div class="w-full bg-white/20 rounded-full h-4 overflow-hidden">
							<div
								class="bg-white h-4 transition-all duration-300 ease-in-out rounded-full"
								style="width: {execution.progress_percentage}%"
							></div>
						</div>
					</div>
				</div>

				<!-- Action Buttons -->
				<div class="flex gap-3">
				{#if execution.status === 'not_started'}
					<button
						onclick={handleStartExecution}
						disabled={saving}
						class="inline-flex items-center gap-2 px-6 py-3 border-2 border-white/30 text-sm font-semibold rounded-xl shadow-lg text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all disabled:opacity-50"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						Start Execution
					</button>
				{:else if execution.status === 'in_progress'}
					<button
						onclick={handleCompleteExecution}
						disabled={saving}
						class="inline-flex items-center gap-2 px-6 py-3 border-2 border-white/30 text-sm font-semibold rounded-xl shadow-lg text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all disabled:opacity-50"
					>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Complete Execution
						</button>
					{/if}
				</div>
			</div>
		</div>

		<!-- Summary Dashboard -->
		<div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
			<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-4">
				<p class="text-xs font-medium text-surface-600 dark:text-surface-400">Total</p>
				<p class="text-2xl font-bold text-surface-900 dark:text-surface-50 mt-1">{summary.total}</p>
			</div>
			<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-4">
				<p class="text-xs font-medium text-surface-600 dark:text-surface-400">✅ Pass</p>
				<p class="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">{summary.pass}</p>
			</div>
			<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-4">
				<p class="text-xs font-medium text-surface-600 dark:text-surface-400">❌ Fail</p>
				<p class="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">{summary.fail}</p>
			</div>
			<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-4">
				<p class="text-xs font-medium text-surface-600 dark:text-surface-400">⚠️ Follow-up</p>
				<p class="text-2xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">{summary.needs_followup}</p>
			</div>
			<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-4">
				<p class="text-xs font-medium text-surface-600 dark:text-surface-400">⚪ Not Tested</p>
				<p class="text-2xl font-bold text-gray-600 dark:text-gray-400 mt-1">{summary.not_tested}</p>
			</div>
		</div>

		<!-- Items List -->
		<div class="space-y-4">
			{#each execution.item_results as itemResult}
				<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
					<div class="p-6">
						<!-- Item Header -->
						<div class="flex items-start justify-between mb-4">
							<div class="flex-1">
								<div class="flex items-center gap-3">
									<span class="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 font-bold">
										{itemResult.checklist_item_order}
									</span>
									<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50">
										{itemResult.checklist_item_title}
									</h3>
								</div>
								{#if itemResult.checklist_item_description}
									<p class="text-sm text-surface-600 dark:text-surface-400 mt-2 ml-13">
										{itemResult.checklist_item_description}
									</p>
								{/if}

								<!-- Linked Items -->
								<div class="flex flex-wrap gap-2 mt-3 ml-13">
									{#if itemResult.control_name}
										<span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
											🛡️ Control: {itemResult.control_name}
										</span>
									{/if}
									{#if itemResult.risk_name}
										<span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400">
											⚠️ Risk: {itemResult.risk_name}
										</span>
									{/if}
									{#if itemResult.policy_name}
										<span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400">
											📋 Policy: {itemResult.policy_name}
										</span>
									{/if}
								</div>
							</div>

							<!-- Current Result Badge -->
							<span class="inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold whitespace-nowrap
								{itemResult.result === 'pass' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
								itemResult.result === 'fail' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' :
								itemResult.result === 'needs_followup' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' :
								itemResult.result === 'not_applicable' ? 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400' :
								'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400'}">
								{getResultChoice(itemResult.result).icon} {getResultChoice(itemResult.result).label}
							</span>
						</div>

					<!-- Result Selector -->
					<div class="mb-4">
						<div class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
							Test Result
						</div>
						<div class="grid grid-cols-2 md:grid-cols-5 gap-2">
								{#each RESULT_CHOICES as choice}
									<button
										type="button"
										onclick={() => handleResultChange(itemResult, choice.value)}
										disabled={saving}
										class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg text-sm font-medium transition-all border-2
											{itemResult.result === choice.value
												? `border-${choice.color}-500 bg-${choice.color}-100 dark:bg-${choice.color}-900/30 text-${choice.color}-800 dark:text-${choice.color}-400`
												: 'border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-700 dark:text-surface-300 hover:border-surface-400 dark:hover:border-surface-500'}
											disabled:opacity-50"
									>
										<span class="text-lg">{choice.icon}</span>
										<span>{choice.label}</span>
									</button>
								{/each}
							</div>
						</div>

						<!-- Comments Section -->
						<div class="space-y-3">
							<div>
								<label for="comments-{itemResult.id}" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
									Comments
								</label>
								<textarea
									id="comments-{itemResult.id}"
									bind:value={itemResult.comments}
									onblur={() => handleCommentSave(itemResult)}
									placeholder="Add auditor comments or observations..."
									rows="3"
									class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
								></textarea>
							</div>

							<div>
								<label for="finding-{itemResult.id}" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
									Finding Summary
								</label>
								<textarea
									id="finding-{itemResult.id}"
									bind:value={itemResult.finding_summary}
									onblur={() => handleCommentSave(itemResult)}
									placeholder="Summarize any issues or findings..."
									rows="2"
									class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
								></textarea>
							</div>
						</div>

						<!-- Audit Trail -->
						{#if itemResult.tested_by_display}
							<div class="mt-4 pt-4 border-t border-surface-200 dark:border-surface-700">
								<p class="text-xs text-surface-600 dark:text-surface-400">
									Tested by <span class="font-semibold">{itemResult.tested_by_display}</span> on {formatDate(itemResult.tested_at || '')}
								</p>
							</div>
						{/if}
					</div>
				</div>
			{/each}
		</div>

		<!-- Execution Notes -->
		{#if execution.notes}
			<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6 mt-6">
				<h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-3">Execution Notes</h3>
				<p class="text-surface-700 dark:text-surface-300">{execution.notes}</p>
			</div>
		{/if}
	{/if}
</div>
