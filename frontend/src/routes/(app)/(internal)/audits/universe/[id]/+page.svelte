<script lang="ts">
	import { page } from '$app/stores';
	import AuditEntityDetail from '$lib/modules/audits/universe/[id]/AuditEntityDetail.svelte';

	// Get the entity ID from the URL parameters
	$: entityId = $page.params.id;
</script>

<svelte:head>
	<title>Audit Entity Details - CISO Assistant</title>
</svelte:head>

<AuditEntityDetail {entityId} />
