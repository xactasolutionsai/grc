<script lang="ts">
	import { run } from 'svelte/legacy';

	import { createEventDispatcher } from 'svelte';
	import { safeTranslate } from '$lib/utils/i18n';

	interface Props {
		text: string;
		id: string;
		choices: (string | null)[];
		disabled?: boolean;
	}

	let { text, id, choices, disabled = false }: Props = $props();

	const dispatch = createEventDispatcher();

	let value = $state(0);
	run(() => {
		dispatch('change', value);
	});
</script>

<div class="flex items-center justify-between gap-4">
	<label for={id} class="text-sm text-surface-700 flex-1 leading-tight {disabled ? 'text-surface-400' : ''}">{safeTranslate(text)}</label>
	<select
		class="w-52 shrink-0 text-sm border border-surface-300 rounded-md px-2.5 py-1.5 bg-white
			disabled:bg-surface-50 disabled:text-surface-400 disabled:border-surface-200 disabled:cursor-not-allowed
			focus:border-primary-400 focus:ring-1 focus:ring-primary-400 transition-colors"
		{id}
		bind:value
		{disabled}
	>
		{#each choices as text, i}
			<option value={i}>{i}{#if text} - {safeTranslate(text)}{/if}</option>
		{/each}
	</select>
</div>
