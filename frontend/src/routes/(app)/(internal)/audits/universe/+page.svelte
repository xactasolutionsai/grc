<script lang="ts">
	import AuditUniverseList from '$lib/modules/audits/universe/AuditUniverseList.svelte';
	import AuditEntityForm from '$lib/modules/audits/universe/AuditEntityForm.svelte';
	import EnhancedModal from '$lib/components/Modals/EnhancedModal.svelte';
	
	let showForm = false;
	let refreshKey = 0;

	function handleEntitySaved() {
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
	<title>Audit Universe - CISO Assistant</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-surface-50 to-surface-100 dark:from-surface-950 dark:to-surface-900">
	<div class="p-6">
		<div class="mb-8">
            <div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 shadow-xl rounded-xl p-8 mb-8">
                <div class="flex justify-between items-center">
                    <div class="flex items-center gap-4">
                        <div class="p-3 bg-white/10 rounded-xl">
                            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                            </svg>
                        </div>
                        <div>
                            <h1 class="text-3xl font-bold text-white">Audit Universe</h1>
                            <p class="text-primary-100 mt-1">Define and manage the full scope of auditable entities in your organization</p>
                        </div>
                    </div>
                    <button on:click={showCreateForm}
                            href="/audits/planning/new"
                            class="inline-flex items-center px-6 py-3 border-2 border-white/30 text-sm font-semibold rounded-xl shadow-lg text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all gap-2"
                    >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                        Add Audit Entity
                    </button>
                </div>
            </div>

			<AuditUniverseList refreshTrigger={refreshKey} />
		</div>
	</div>

	<!-- Popup Modal -->
	<EnhancedModal 
		bind:open={showForm} 
		title="Add Audit Entity" 
		maxWidth="4xl"
		onClose={closeForm}
	>
		<AuditEntityForm onSaved={handleEntitySaved} />
	</EnhancedModal>
</div>
