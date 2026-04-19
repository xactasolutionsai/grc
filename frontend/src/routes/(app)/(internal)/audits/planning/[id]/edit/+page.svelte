<script lang="ts">
	import { page } from '$app/state';
	import AuditPlanForm from '$lib/modules/audits/planning/AuditPlanForm.svelte';
	import { goto } from '$app/navigation';

	let planId = $derived(parseInt(page.params.id));

	function handleSaved() {
		// Redirect to plan detail
		goto(`/audits/planning/${planId}`);
	}
</script>

<AuditPlanForm {planId} onSaved={handleSaved} />
