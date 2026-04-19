<script lang="ts">
	import ModelForm from '$lib/components/Forms/ModelForm.svelte';
	import type { SuperValidated } from 'sveltekit-superforms';
	import type { AnyZodObject } from 'zod';
	import { getModalStore, type ModalStore } from './stores';
	import type { ModelInfo } from '$lib/utils/types';

	const modalStore: ModalStore = getModalStore();

	let closeModal = true;

	// Base Classes - Enhanced
	const cBase = 'card bg-surface-50 dark:bg-surface-900 w-full max-w-3xl shadow-2xl overflow-hidden rounded-xl';
	const cHeader = 'text-2xl font-bold text-surface-900 dark:text-surface-50';

	interface Props {
		/** Exposes parent props to this component. */
		parent: any;
		form: SuperValidated<AnyZodObject>;
		model: ModelInfo;
		invalidateAll?: boolean; // set to false to keep form data using muliple forms on a page
		formAction?: string;
		context?: string;
		object?: Record<string, any>;
		suggestions?: { [key: string]: any };
		selectOptions?: Record<string, any>;
		debug?: boolean;
	}

	let {
		parent,
		form,
		model,
		invalidateAll = true,
		formAction = '?/update',
		context = 'default',
		object = {},
		suggestions = {},
		selectOptions = {},
		debug = false
	}: Props = $props();
</script>

{#if $modalStore[0]}
	<div class="modal-example-form {cBase}">
		<!-- Modal Header -->
		<div class="flex items-center justify-between border-b border-surface-200 dark:border-surface-700 px-6 py-5">
			<header class={cHeader} data-testid="modal-title">
				{$modalStore[0].title ?? '(title missing)'}
			</header>
			<button
				type="button"
				class="text-surface-400 hover:text-surface-600 dark:hover:text-surface-200 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-full p-1.5 transition-colors duration-200 hover:bg-surface-100 dark:hover:bg-surface-800"
				onclick={parent.onClose}
				aria-label="Close modal"
			>
				<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>
		<!-- Modal Body -->
		<div class="px-6 py-6">
			<ModelForm
			customNameDescription
			{form}
			{object}
			{suggestions}
			{parent}
			action={formAction}
			{invalidateAll}
			{model}
			{closeModal}
			{context}
			caching={true}
				{selectOptions}
				{debug}
			/>
		</div>
	</div>
{/if}
