<script lang="ts">
	import { page } from '$app/state';
	import AuditPlanForm from '$lib/modules/audits/planning/AuditPlanForm.svelte';
	import { goto } from '$app/navigation';

	let entityId = $derived(page.url.searchParams.get('entity') ? parseInt(page.url.searchParams.get('entity')!) : null);

	function handleSaved() {
		// Redirect to plans list
		goto('/audits/planning');
	}
</script>

<AuditPlanForm {entityId} onSaved={handleSaved} />
