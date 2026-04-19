<script>
	import AuditEngagementDetail from '$lib/modules/audits/engagements/AuditEngagementDetail.svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	$: engagementId = $page.params.id;

	function handleEdit(engagement) {
		goto(`/audits/engagements/${engagement.id}/edit`);
	}

	function handleClose() {
		goto('/audits/engagements');
	}
</script>

<svelte:head>
	<title>Engagement Details - CISO Assistant</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<AuditEngagementDetail
		{engagementId}
		onEdit={handleEdit}
		onClose={handleClose}
	/>
</div>
