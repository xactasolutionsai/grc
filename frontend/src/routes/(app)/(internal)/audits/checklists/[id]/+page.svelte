<script lang="ts">
	import { page } from '$app/stores';
	import ChecklistDetail from '$lib/modules/audits/checklists/ChecklistDetail.svelte';

	const checklistId = $derived($page.data.checklistId);
</script>

<ChecklistDetail {checklistId} />
