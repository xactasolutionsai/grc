<script lang="ts">
	import { page } from '$app/stores';
	import ChecklistForm from '$lib/modules/audits/checklists/ChecklistForm.svelte';

	const checklistId = $derived($page.data.checklistId);
</script>

<ChecklistForm {checklistId} />
