<script lang="ts">
	import type { urlModel } from '$lib/utils/types';

	import { m } from '$paraglide/messages';

	const modalStore: ModalStore = getModalStore();

	import { superForm } from 'sveltekit-superforms';

	// Base Classes - Enhanced
	const cBase = 'card bg-surface-50 dark:bg-surface-900 w-full max-w-3xl shadow-2xl overflow-hidden rounded-xl';
	const cHeader = 'text-2xl font-bold text-surface-900 dark:text-surface-50';
	const cForm = 'space-y-4';
	const cActions = 'flex justify-end gap-3';

	import SuperDebug from 'sveltekit-superforms';
	import type { ComponentType } from 'svelte';
	import { enhance } from '$app/forms';
	import { getModalStore, type ModalStore } from './stores';
	interface Props {
		/** Exposes parent props to this component. */
		parent: any;
		_form?: any;
		URLModel?: urlModel | '';
		id?: string;
		formAction?: string;
		bodyComponent: ComponentType | undefined;
		bodyProps?: Record<string, unknown>;
		debug?: boolean;
	}

	let {
		parent,
		_form = {},
		URLModel = '',
		id = '',
		formAction = '',
		bodyComponent,
		bodyProps = {},
		debug = false
	}: Props = $props();

	let form: any = null;
	
	if (_form) {
		const formResult = superForm(_form, {
			dataType: 'json',
			id: `confirm-modal-form-${crypto.randomUUID()}`
		});
		form = formResult.form;
	}

	let userInput = $state('');
</script>

{#if $modalStore[0]}
	<div class="modal-example-form {cBase}">
		<!-- Modal Header -->
		<div class="border-b border-surface-200 dark:border-surface-700 px-6 py-5">
			<header class={cHeader}>{$modalStore[0].title ?? '(title missing)'}</header>
		</div>
		<!-- Modal Body -->
		<div class="px-6 py-6 space-y-4">
			<article class="text-surface-700 dark:text-surface-300">{$modalStore[0].body ?? '(body missing)'}</article>

			<div>
				<p class="text-error-500 font-bold mb-2">{m.confirmYes()}</p>
				<input
					type="text"
					data-testid="delete-prompt-confirm-textfield"
					bind:value={userInput}
					placeholder={m.confirmYesPlaceHolder()}
					class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-surface-50 dark:bg-surface-800"
				/>
			</div>

			{#if bodyComponent}
				{@const SvelteComponent = bodyComponent}
				<div class="max-h-96 overflow-y-auto scroll card">
					<SvelteComponent {...bodyProps} />
				</div>
			{/if}
		</div>
		<!-- Modal Footer -->
		<div class="border-t border-surface-200 dark:border-surface-700 px-6 py-4">
			{#if _form && Object.keys(_form).length > 0}
				<form method="POST" action={formAction} use:enhance class="modal-form {cForm}">
					<footer class="modal-footer {cActions}">
						<button type="button" class="btn {parent.buttonNeutral}" onclick={parent.onClose}
							>{m.cancel()}</button
						>
						<input type="hidden" name="urlmodel" value={URLModel} />
						<input type="hidden" name="id" value={id} />
						<button
							class="btn preset-filled-error-500"
							type="submit"
							data-testid="delete-prompt-confirm-button"
							onclick={parent.onConfirm}
							disabled={!userInput || userInput.trim().toLowerCase() !== m.yes().toLowerCase()}
						>
							{m.submit()}
						</button>
					</footer>
				</form>

				{#if debug === true}
					<SuperDebug data={$form} />
				{/if}
			{:else}
				<footer class="modal-footer {cActions}">
					<button type="button" class="btn {parent.buttonNeutral}" onclick={parent.onClose}
						>{m.cancel()}</button
					>
					<button
						class="btn preset-filled-error-500"
						type="button"
						onclick={parent.onConfirm}
						disabled={!userInput || userInput.trim().toLowerCase() !== m.yes().toLowerCase()}
					>
						{m.submit()}
					</button>
				</footer>
			{/if}
		</div>
	</div>
{/if}
