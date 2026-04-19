<script lang="ts">
	import { submitForReview, approveWorkpaper, rejectWorkpaper } from './api.js';
	import EnhancedModal from '$lib/components/Modals/EnhancedModal.svelte';

	interface Props {
		workpaper: any;
		onActionComplete?: () => void;
	}

	let { workpaper, onActionComplete = () => {} }: Props = $props();

	let processing = $state(false);
	let showRejectModal = $state(false);
	let rejectReason = $state('');
	let approveComments = $state('');
	let showApproveModal = $state(false);
	let error = $state<string | null>(null);

	async function handleSubmitForReview() {
		if (confirm('Submit this workpaper for review?')) {
			try {
				processing = true;
				error = null;
				await submitForReview(workpaper.id);
				onActionComplete();
			} catch (err: any) {
				console.error('Error submitting for review:', err);
				error = err.message;
			} finally {
				processing = false;
			}
		}
	}

	async function handleApprove() {
		showApproveModal = true;
	}

	async function confirmApprove() {
		try {
			processing = true;
			error = null;
			await approveWorkpaper(workpaper.id, approveComments);
			showApproveModal = false;
			approveComments = '';
			onActionComplete();
		} catch (err: any) {
			console.error('Error approving workpaper:', err);
			error = err.message;
		} finally {
			processing = false;
		}
	}

	function handleReject() {
		showRejectModal = true;
	}

	async function confirmReject() {
		if (!rejectReason.trim()) {
			alert('Please provide a reason for rejection');
			return;
		}

		try {
			processing = true;
			error = null;
			await rejectWorkpaper(workpaper.id, rejectReason);
			showRejectModal = false;
			rejectReason = '';
			onActionComplete();
		} catch (err: any) {
			console.error('Error rejecting workpaper:', err);
			error = err.message;
		} finally {
			processing = false;
		}
	}
</script>

<div class="space-y-3">
	{#if error}
		<div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-lg p-3 flex items-start gap-2">
			<svg class="h-4 w-4 text-error-600 dark:text-error-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<div class="text-error-800 dark:text-error-200 text-sm">{error}</div>
		</div>
	{/if}

	<div class="flex flex-wrap gap-2">
		{#if workpaper.can_be_reviewed}
			<button
				onclick={handleSubmitForReview}
				disabled={processing}
				class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
			>
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
				</svg>
				Submit for Review
			</button>
		{/if}

		{#if workpaper.can_be_approved}
			<button
				onclick={handleApprove}
				disabled={processing}
				class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
			>
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				Approve
			</button>

			<button
				onclick={handleReject}
				disabled={processing}
				class="px-4 py-2 bg-error-600 text-white rounded-lg hover:bg-error-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
			>
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
				Reject
			</button>
		{/if}
	</div>
</div>

<!-- Approve Modal -->
<EnhancedModal bind:open={showApproveModal} title="Approve Workpaper" maxWidth="md">
	{#snippet children()}
		<div class="space-y-4">
			<div>
				<label for="approve-comments" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
					Comments (optional)
				</label>
				<textarea
					id="approve-comments"
					bind:value={approveComments}
					rows="3"
					class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
					placeholder="Add any comments about the approval..."
				></textarea>
			</div>

			<div class="flex justify-end gap-3 pt-2">
				<button
					onclick={() => showApproveModal = false}
					type="button"
					class="px-4 py-2 border border-surface-300 dark:border-surface-600 rounded-lg text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-700 transition-colors"
				>
					Cancel
				</button>
				<button
					onclick={confirmApprove}
					type="button"
					disabled={processing}
					class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
				>
					{#if processing}
						<svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
					{:else}
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
						</svg>
					{/if}
					Approve
				</button>
			</div>
		</div>
	{/snippet}
</EnhancedModal>

<!-- Reject Modal -->
<EnhancedModal bind:open={showRejectModal} title="Reject Workpaper" maxWidth="md">
	{#snippet children()}
		<div class="space-y-4">
			<div>
				<label for="reject-reason" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
					Reason <span class="text-error-500">*</span>
				</label>
				<textarea
					id="reject-reason"
					bind:value={rejectReason}
					rows="4"
					required
					class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
					placeholder="Please provide a reason for rejecting this workpaper..."
				></textarea>
			</div>

			<div class="flex justify-end gap-3 pt-2">
				<button
					onclick={() => showRejectModal = false}
					type="button"
					class="px-4 py-2 border border-surface-300 dark:border-surface-600 rounded-lg text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-700 transition-colors"
				>
					Cancel
				</button>
				<button
					onclick={confirmReject}
					type="button"
					disabled={processing || !rejectReason.trim()}
					class="px-4 py-2 bg-error-600 text-white rounded-lg hover:bg-error-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
				>
					{#if processing}
						<svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
					{:else}
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					{/if}
					Reject
				</button>
			</div>
		</div>
	{/snippet}
</EnhancedModal>

