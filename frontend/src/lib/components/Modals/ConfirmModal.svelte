<script lang="ts">
	import type { urlModel } from '$lib/utils/types';
	import SuperDebug from 'sveltekit-superforms';
	import type { ComponentType } from 'svelte';
	import { getModalStore, type ModalStore } from './stores';
	import { m } from '$paraglide/messages';
	import { superForm } from 'sveltekit-superforms';
	import SuperForm from '$lib/components/Forms/Form.svelte';

	const modalStore: ModalStore = getModalStore();

	// Base Classes - Enhanced
	const cBase = 'card bg-surface-50 dark:bg-surface-900 w-full max-w-3xl shadow-2xl overflow-hidden rounded-xl';
	const cHeader = 'text-2xl font-bold text-surface-900 dark:text-surface-50';
	const cForm = 'space-y-4';
	const cActions = 'flex justify-end gap-3';

	interface Props {
		/** Exposes parent props to this component. */
		parent: any;
		_form?: any;
		URLModel?: urlModel | '';
		id?: string;
		formAction: string;
		bodyComponent: ComponentType | undefined;
		bodyProps?: Record<string, unknown>;
		debug?: boolean;
		schema?: any;
	}

	let {
		parent,
		_form = {},
		URLModel = '',
		id = '',
		formAction,
		bodyComponent,
		bodyProps = {},
		debug = false,
		schema
	}: Props = $props();

	const { form } = superForm(_form, {
		dataType: 'json',
		id: `confirm-modal-form-${crypto.randomUUID()}`
	});
</script>

{#if $modalStore[0]}
	<div class="modal-example-form {cBase}">
		<!-- Modal Header -->
		<div class="border-b border-surface-200 dark:border-surface-700 px-6 py-5">
			<header class={cHeader}>{$modalStore[0].title ?? '(title missing)'}</header>
		</div>
		<!-- Modal Body -->
		<div class="px-6 py-6">
			<article class="text-surface-700 dark:text-surface-300">{$modalStore[0].body ?? '(body missing)'}</article>
			{#if bodyComponent}
				{@const SvelteComponent = bodyComponent}
				<div class="max-h-96 overflow-y-auto scroll card mt-4">
					<SvelteComponent {...bodyProps} />
				</div>
			{/if}
			<!-- Enable for debugging: -->
			<SuperForm
				dataType="json"
				action={formAction}
				data={_form}
				class="modal-form {cForm}"
				validators={schema}
			>
				{#if debug === true}
					<SuperDebug data={$form} />
				{/if}
			</SuperForm>
		</div>
		<!-- Modal Footer -->
		<div class="border-t border-surface-200 dark:border-surface-700 px-6 py-4">
			<footer class="modal-footer {cActions}">
				<button type="button" class="btn {parent.buttonNeutral}" onclick={parent.onClose}>{m.cancel()}</button>
				<input type="hidden" name="urlmodel" value={URLModel} />
				<input type="hidden" name="id" value={id} />
				<button class="btn preset-filled-error-500" type="submit" onclick={parent.onConfirm}>{m.submit()}</button>
			</footer>
		</div>
	</div>
{/if}
