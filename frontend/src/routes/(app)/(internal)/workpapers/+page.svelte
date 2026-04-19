<script lang="ts">
	import { onMount } from 'svelte';
	import { pageTitle } from '$lib/utils/stores';
	import WorkpaperList from '$lib/modules/workpapers/WorkpaperList.svelte';
	import WorkpaperForm from '$lib/modules/workpapers/WorkpaperForm.svelte';
	import EnhancedModal from '$lib/components/Modals/EnhancedModal.svelte';
	
	let showForm = false;
	let refreshKey = 0;

	// Set page title for breadcrumbs
	onMount(() => {
		pageTitle.set('Workpapers & Evidence');
	});

	function handleWorkpaperSaved() {
		showForm = false;
		refreshKey += 1; // This will trigger a refresh of the list
	}

	function showCreateForm() {
		showForm = true;
	}

	function closeForm() {
		showForm = false;
	}
</script>

<svelte:head>
	<title>Workpapers & Evidence - CISO Assistant</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-surface-50 to-surface-100 dark:from-surface-950 dark:to-surface-900">
	<div class="p-6">
		<div class="mb-8">
			<div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 shadow-xl rounded-xl p-8 mb-8">
				<div class="flex justify-between items-center">
					<div class="flex items-center gap-4">
						<div class="p-3 bg-white/10 rounded-xl">
							<svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
						</div>
						<div>
							<h1 class="text-3xl font-bold text-white">Workpapers & Evidence</h1>
							<p class="text-primary-100 mt-1">Manage audit workpapers and evidence with approval workflows</p>
						</div>
					</div>
					<button 
						on:click={showCreateForm}
						class="inline-flex items-center px-6 py-3 border-2 border-white/30 text-sm font-semibold rounded-xl shadow-lg text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all gap-2"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
						Add Workpaper
					</button>
				</div>
			</div>

			<WorkpaperList refreshTrigger={refreshKey} />
		</div>
	</div>

	<!-- Popup Modal -->
	<EnhancedModal 
		bind:open={showForm} 
		title="Add Workpaper" 
		maxWidth="4xl"
		onClose={closeForm}
	>
		{#snippet children()}
			<WorkpaperForm onSaved={handleWorkpaperSaved} />
		{/snippet}
	</EnhancedModal>
</div>

