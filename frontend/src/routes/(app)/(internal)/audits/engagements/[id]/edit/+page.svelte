<script>
	import AuditEngagementForm from '$lib/modules/audits/engagements/AuditEngagementForm.svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	$: engagementId = $page.params.id;

	function handleSaved() {
		goto(`/audits/engagements/${engagementId}`);
	}

	function handleCancel() {
		goto(`/audits/engagements/${engagementId}`);
	}
</script>

<svelte:head>
	<title>Edit Engagement - CISO Assistant</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<AuditEngagementForm 
		{engagementId}
		onSaved={handleSaved}
		onCancel={handleCancel}
	/>
</div>
