<script lang="ts">
	import { page } from '$app/state';
	import AuditPlanDetail from '$lib/modules/audits/planning/AuditPlanDetail.svelte';

	let planId = $derived(parseInt(page.params.id));
</script>

<AuditPlanDetail {planId} />
