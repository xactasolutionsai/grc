<script lang="ts">
	import { get, type Writable } from 'svelte/store';
	import { callAI, AIClientError, type ExpandTextResult } from '$lib/utils/ai';
	import { getToastStore } from '$lib/components/Toast/stores';
	import { m } from '$paraglide/messages';
	import AIAssistButton from './AIAssistButton.svelte';

	interface Props {
		/** The SuperForm instance (passed as `form` from parent). */
		form: any;
		/** Which field to expand & write back to. Defaults to 'description'. */
		field?: string;
		/** Optional field that holds a short context string (e.g. the name). */
		contextField?: string;
		/** Field type for prompt context. */
		fieldType?: 'risk' | 'control' | 'policy' | 'finding' | 'generic';
		/** Minimum characters in the source field before enabling. */
		minLength?: number;
		/** Optional override label. */
		label?: string;
		updated_fields?: Set<string>;
	}

	let {
		form,
		field = 'description',
		contextField = 'name',
		fieldType = 'generic',
		minLength = 3,
		label,
		updated_fields = new Set<string>()
	}: Props = $props();

	const toastStore = getToastStore();
	let loading = $state(false);

	async function expand() {
		const store = form?.form as Writable<Record<string, any>> | undefined;
		if (!store) return;
		const data = get(store) ?? {};
		const text = (data[field] ?? '').toString();
		const ctx = contextField ? (data[contextField] ?? '').toString() : '';

		if (text.trim().length < minLength) {
			toastStore.trigger({
				message: m.expandWithAI() + ': ' + field,
				background: 'variant-filled-warning'
			});
			return;
		}

		loading = true;
		try {
			const result = await callAI<ExpandTextResult>('expand-text', {
				text,
				field_type: fieldType,
				context: ctx
			});
			store.update((d: Record<string, any>) => {
				const next = { ...d };
				next[field] = result.expanded;
				updated_fields.add(field);
				return next;
			});
		} catch (err) {
			const msg =
				err instanceof AIClientError && err.code === 'parse_error'
					? m.aiParseError()
					: err instanceof Error
						? err.message
						: m.aiError();
			toastStore.trigger({ message: msg, background: 'variant-filled-error' });
		} finally {
			loading = false;
		}
	}
</script>

<div class="flex items-center gap-2">
	<AIAssistButton
		label={label ?? m.expandWithAI()}
		title={m.expandWithAI()}
		{loading}
		onclick={expand}
		variant="subtle"
		size="sm"
	/>
	{#if loading}
		<span class="text-xs text-gray-500">{m.aiThinking()}</span>
	{/if}
</div>
