<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { pageTitle } from '$lib/utils/stores';
	import WorkpaperCard from '$lib/modules/workpapers/WorkpaperCard.svelte';

	let workpaperId = $derived(page.params.id);

	// Set page title for breadcrumbs
	onMount(() => {
		pageTitle.set('Workpaper Details');
	});

	function handleUpdate() {
		// Refresh the page to get updated data
		window.location.reload();
	}

	function goBack() {
		goto('/workpapers');
	}
</script>

<svelte:head>
	<title>Workpaper Details - CISO Assistant</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-surface-50 to-surface-100 dark:from-surface-950 dark:to-surface-900">
	<div class="p-6">
		<div class="mb-6">
			<button
				onclick={goBack}
				class="inline-flex items-center gap-2 text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-50 transition-colors"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
				</svg>
				Back to Workpapers
			</button>
		</div>

		<WorkpaperCard {workpaperId} onUpdate={handleUpdate} />
	</div>
</div>
