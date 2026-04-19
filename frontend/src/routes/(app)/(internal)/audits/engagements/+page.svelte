<script>
	import AuditEngagementList from '$lib/modules/audits/engagements/AuditEngagementList.svelte';
	import AuditEngagementForm from '$lib/modules/audits/engagements/AuditEngagementForm.svelte';
	import { page } from '$app/stores';

	let showCreateForm = false;
	let editingEngagement = null;

	function handleEngagementSaved() {
		showCreateForm = false;
		editingEngagement = null;
	}

	function handleEditEngagement(engagement) {
		editingEngagement = engagement;
		showCreateForm = true;
	}

	function handleCancel() {
		showCreateForm = false;
		editingEngagement = null;
	}
</script>

<svelte:head>
	<title>Audit Engagements - CISO Assistant</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	{#if showCreateForm}
       <div>
           <AuditEngagementForm
                   engagementId={editingEngagement?.id}
                   onSaved={handleEngagementSaved}
                   onCancel={handleCancel}
           />
       </div>
	{:else}
        <div>
            <AuditEngagementList
                    onEdit={handleEditEngagement}
                    onCreate={() => showCreateForm = true}
            />
        </div>
	{/if}
</div>
