<script lang="ts">
	import { onMount } from 'svelte';
	import { getWorkpaper, getApprovalHistory } from './api.js';
	import WorkpaperActions from './WorkpaperActions.svelte';

	export let workpaperId: string | number;
	export let onUpdate = () => {};

	let workpaper: any = null;
	let approvalHistory: any[] = [];
	let loading = true;
	let error: string | null = null;

	onMount(() => {
		loadWorkpaper();
	});

	async function loadWorkpaper() {
		try {
			loading = true;
			error = null;
			workpaper = await getWorkpaper(workpaperId);

			// Load approval history
			try {
				approvalHistory = await getApprovalHistory(workpaperId);
			} catch (err) {
				console.error('Error loading approval history:', err);
			}
		} catch (err: any) {
			console.error('Error loading workpaper:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	}

	function formatDate(dateString: string | null) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleString();
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

	function handleActionComplete() {
		loadWorkpaper();
		onUpdate();
	}
</script>

{#if loading}
	<div class="flex justify-center items-center py-12">
		<div class="flex flex-col items-center gap-3">
			<svg class="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
			</svg>
			<div class="text-surface-600 font-medium">Loading workpaper...</div>
		</div>
	</div>
{:else if error}
	<div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-4 flex items-start gap-3">
		<svg class="h-5 w-5 text-error-600 dark:text-error-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
		</svg>
		<div class="text-error-800 dark:text-error-200">{error}</div>
	</div>
{:else if workpaper}
	<div class="space-y-6">
		<!-- Header Card -->
		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<div class="flex items-start justify-between mb-4">
				<div class="flex items-start gap-3">
					<span class="text-4xl">{getTypeIcon(workpaper.workpaper_type)}</span>
					<div>
						<h1 class="text-2xl font-bold text-surface-900 dark:text-surface-50">{workpaper.title}</h1>
						<span class="text-sm px-3 py-1 rounded-full {getStatusColor(workpaper.status)} inline-block mt-2">
							{workpaper.status.charAt(0).toUpperCase() + workpaper.status.slice(1)}
						</span>
					</div>
				</div>
			</div>

			{#if workpaper.description}
				<p class="text-surface-600 dark:text-surface-300 mb-4">{workpaper.description}</p>
			{/if}

			<!-- Workflow Actions -->
			<WorkpaperActions {workpaper} onActionComplete={handleActionComplete} />
		</div>

		<!-- File/Link Information -->
		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4">File Information</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#if workpaper.file_url}
					<div>
						<span class="text-sm font-medium text-surface-600 dark:text-surface-400">File</span>
						<div class="mt-1">
							<a href={workpaper.file_url} target="_blank" class="text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-2">
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								</svg>
								{workpaper.file_name || 'Download File'}
							</a>
						</div>
					</div>
					{#if workpaper.file_size}
						<div>
							<span class="text-sm font-medium text-surface-600 dark:text-surface-400">File Size</span>
							<div class="mt-1 text-surface-900 dark:text-surface-50">{formatFileSize(workpaper.file_size)}</div>
						</div>
					{/if}
				{/if}

				{#if workpaper.external_link}
					<div>
						<span class="text-sm font-medium text-surface-600 dark:text-surface-400">External Link</span>
						<div class="mt-1">
							<a href={workpaper.external_link} target="_blank" class="text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-2">
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
								</svg>
								{workpaper.external_link}
							</a>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Metadata Card -->
		<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
			<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4">Details</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#if workpaper.uploaded_by_display}
					<div>
						<span class="text-sm font-medium text-surface-600 dark:text-surface-400">Uploaded By</span>
						<div class="mt-1 text-surface-900 dark:text-surface-50">{workpaper.uploaded_by_display.name}</div>
					</div>
				{/if}
				<div>
					<span class="text-sm font-medium text-surface-600 dark:text-surface-400">Created At</span>
					<div class="mt-1 text-surface-900 dark:text-surface-50">{formatDate(workpaper.created_at)}</div>
				</div>
				{#if workpaper.reviewer_display}
					<div>
						<span class="text-sm font-medium text-surface-600 dark:text-surface-400">Reviewed By</span>
						<div class="mt-1 text-surface-900 dark:text-surface-50">{workpaper.reviewer_display.name}</div>
					</div>
					<div>
						<span class="text-sm font-medium text-surface-600 dark:text-surface-400">Reviewed At</span>
						<div class="mt-1 text-surface-900 dark:text-surface-50">{formatDate(workpaper.reviewed_at)}</div>
					</div>
				{/if}
				{#if workpaper.approver_display}
					<div>
						<span class="text-sm font-medium text-surface-600 dark:text-surface-400">Approved By</span>
						<div class="mt-1 text-surface-900 dark:text-surface-50">{workpaper.approver_display.name}</div>
					</div>
					<div>
						<span class="text-sm font-medium text-surface-600 dark:text-surface-400">Approved At</span>
						<div class="mt-1 text-surface-900 dark:text-surface-50">{formatDate(workpaper.approved_at)}</div>
					</div>
				{/if}
			</div>

			{#if workpaper.tags && workpaper.tags.length > 0}
				<div class="mt-4">
					<span class="text-sm font-medium text-surface-600 dark:text-surface-400">Tags</span>
					<div class="mt-2 flex flex-wrap gap-2">
						{#each workpaper.tags as tag}
							<span class="px-2 py-1 rounded-md text-sm bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-200">
								{tag}
							</span>
						{/each}
					</div>
				</div>
			{/if}

			{#if workpaper.rejection_reason}
				<div class="mt-4 p-3 bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-lg">
					<span class="text-sm font-medium text-error-800 dark:text-error-200">Rejection Reason:</span>
					<p class="mt-1 text-sm text-error-700 dark:text-error-300">{workpaper.rejection_reason}</p>
				</div>
			{/if}
		</div>

		<!-- Approval History Card -->
		{#if approvalHistory.length > 0}
			<div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 p-6">
				<h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 mb-4">Approval History</h2>
				<div class="space-y-3">
					{#each approvalHistory as record}
						<div class="flex items-start gap-3 p-3 bg-surface-50 dark:bg-surface-900/50 rounded-lg">
							<div class="flex-shrink-0 mt-1">
								{#if record.action === 'approved'}
									<div class="h-8 w-8 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
										<svg class="h-4 w-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
										</svg>
									</div>
								{:else if record.action === 'rejected'}
									<div class="h-8 w-8 rounded-full bg-error-100 dark:bg-error-900/30 flex items-center justify-center">
										<svg class="h-4 w-4 text-error-600 dark:text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
										</svg>
									</div>
								{:else}
									<div class="h-8 w-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
										<svg class="h-4 w-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
										</svg>
									</div>
								{/if}
							</div>
							<div class="flex-1">
								<div class="flex items-center justify-between">
									<span class="font-medium text-surface-900 dark:text-surface-50">{record.action_display}</span>
									<span class="text-xs text-surface-500 dark:text-surface-400">{formatDate(record.created_at)}</span>
								</div>
								{#if record.action_by_display}
									<div class="text-sm text-surface-600 dark:text-surface-300">by {record.action_by_display.name}</div>
								{/if}
								{#if record.comments}
									<div class="mt-1 text-sm text-surface-600 dark:text-surface-300 italic">"{record.comments}"</div>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</div>
{/if}
