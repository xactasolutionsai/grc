<script lang="ts">
	import { callAI, AIClientError, type GenerateControlsResult, type GeneratedControl } from '$lib/utils/ai';
	import { getToastStore } from '$lib/components/Toast/stores';
	import { m } from '$paraglide/messages';
	import AIAssistButton from '$lib/components/AI/AIAssistButton.svelte';

	interface Props {
		/** Skeleton modal parent prop (injected). */
		parent: { onClose: (event?: unknown) => void };
		onApply?: (control: GeneratedControl) => void;
	}

	let { parent, onApply }: Props = $props();

	const toastStore = getToastStore();
	let riskDescription = $state('');
	let loading = $state(false);
	let results = $state<GeneratedControl[] | null>(null);

	async function run() {
		const text = riskDescription.trim();
		if (text.length < 3) {
			toastStore.trigger({
				message: m.generateControlsFromRisk() + ': ' + m.riskDescription(),
				background: 'variant-filled-warning'
			});
			return;
		}
		loading = true;
		try {
			const r = await callAI<GenerateControlsResult>('generate-controls', {
				risk_description: text
			});
			results = r.controls ?? [];
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

	function copy(text: string) {
		navigator.clipboard?.writeText(text).catch(() => {});
	}
</script>

<div
	class="modal block space-y-3 w-[min(92vw,720px)] bg-white p-6 rounded-md shadow-lg"
	data-testid="ai-generate-controls-modal"
>
	<header class="flex items-center justify-between">
		<h3 class="h3 font-semibold">{m.generateControlsFromRisk()}</h3>
		<button
			type="button"
			class="text-gray-500 hover:text-gray-800"
			onclick={() => parent.onClose()}
		>×</button>
	</header>

	<div>
		<label class="label text-sm font-medium" for="ai-gen-controls-input">
			{m.riskDescription()}
		</label>
		<textarea
			id="ai-gen-controls-input"
			class="textarea w-full border rounded-md p-2 text-sm"
			rows="4"
			bind:value={riskDescription}
			placeholder="Ransomware attack via phishing email on finance team..."
		></textarea>
	</div>

	<div class="flex items-center gap-2">
		<AIAssistButton
			label={m.generateControls()}
			{loading}
			onclick={run}
			variant="primary"
		/>
		{#if loading}
			<span class="text-xs text-gray-500">{m.aiThinking()}</span>
		{/if}
	</div>

	{#if results && results.length}
		<div class="space-y-2 max-h-[45vh] overflow-y-auto pr-1">
			<div class="text-xs font-medium text-gray-700">{m.aiResultsControls()}</div>
			{#each results as control}
				<div class="border rounded-md p-3 bg-gray-50">
					<div class="flex items-start justify-between gap-3">
						<div class="flex-1">
							<div class="font-semibold">{control.name}</div>
							<div class="text-sm text-gray-700 mt-1">{control.description}</div>
							<div class="text-xs text-gray-500 mt-1">
								<span class="chip px-2 py-0.5 rounded-full bg-primary-100">
									{control.control_type}
								</span>
							</div>
							{#if control.implementation_guidance}
								<details class="mt-2">
									<summary class="cursor-pointer text-xs text-primary-700">
										Implementation guidance
									</summary>
									<div class="text-sm text-gray-700 mt-1 whitespace-pre-wrap">
										{control.implementation_guidance}
									</div>
								</details>
							{/if}
						</div>
						<div class="flex flex-col gap-1 shrink-0">
							{#if onApply}
								<button
									type="button"
									class="btn btn-sm preset-filled-primary-500"
									onclick={() => onApply?.(control)}
								>
									{m.addToForm()}
								</button>
							{/if}
							<button
								type="button"
								class="btn btn-sm preset-tonal"
								onclick={() =>
									copy(
										`${control.name}\n\n${control.description}\n\n${control.implementation_guidance ?? ''}`
									)}
							>
								Copy
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{:else if results && results.length === 0}
		<div class="text-sm text-gray-500">{m.noData()}</div>
	{/if}

	<footer class="flex justify-end">
		<button
			type="button"
			class="btn bg-gray-300"
			onclick={() => parent.onClose()}
		>
			{m.cancel()}
		</button>
	</footer>
</div>
