<script lang="ts">
	import ChecklistExecutionView from '$lib/modules/audits/checklists/ChecklistExecutionView.svelte';

	let { data } = $props();
</script>

<ChecklistExecutionView executionId={data.executionId} />
