<script lang="ts">
	import { callAI, AIClientError, type DashboardInsightsResult } from '$lib/utils/ai';
	import { getToastStore } from '$lib/components/Toast/stores';
	import { m } from '$paraglide/messages';
	import AIAssistButton from './AIAssistButton.svelte';

	const toastStore = getToastStore();
	let loading = $state(false);
	let result = $state<DashboardInsightsResult | null>(null);
	let error = $state<string | null>(null);

	async function generate() {
		loading = true;
		error = null;
		try {
			result = await callAI<DashboardInsightsResult>('dashboard-insights', {});
		} catch (err) {
			const msg =
				err instanceof AIClientError && err.code === 'parse_error'
					? m.aiParseError()
					: err instanceof Error
						? err.message
						: m.aiError();
			error = msg;
			toastStore.trigger({ message: msg, background: 'variant-filled-error' });
		} finally {
			loading = false;
		}
	}
</script>

<section
	class="border border-primary-200 bg-primary-50/40 rounded-lg p-4 mb-4"
	data-testid="ai-insights-panel"
>
	<header class="flex items-center justify-between mb-3">
		<div>
			<div class="font-semibold text-primary-900">{m.aiInsights()}</div>
			<div class="text-xs text-gray-600">
				{m.executiveSummary()} · powered by local Ollama
			</div>
		</div>
		<AIAssistButton
			label={m.generateInsights()}
			{loading}
			onclick={generate}
			variant="primary"
		/>
	</header>

	{#if loading}
		<div class="text-sm text-gray-700">{m.aiThinking()}</div>
	{:else if error}
		<div class="text-sm text-red-700">{error}</div>
	{:else if result}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
			<div class="bg-white rounded-md p-3 border">
				<div class="font-semibold mb-1">{m.topRisks()}</div>
				{#if result.top_risks?.length}
					<ul class="list-disc ml-5 space-y-0.5">
						{#each result.top_risks as bullet}
							<li>{bullet}</li>
						{/each}
					</ul>
				{:else}
					<div class="text-xs text-gray-500">{m.noData()}</div>
				{/if}
			</div>
			<div class="bg-white rounded-md p-3 border">
				<div class="font-semibold mb-1">{m.complianceGaps()}</div>
				{#if result.compliance_gaps?.length}
					<ul class="list-disc ml-5 space-y-0.5">
						{#each result.compliance_gaps as bullet}
							<li>{bullet}</li>
						{/each}
					</ul>
				{:else}
					<div class="text-xs text-gray-500">{m.noData()}</div>
				{/if}
			</div>
			<div class="bg-white rounded-md p-3 border">
				<div class="font-semibold mb-1">{m.recommendedActions()}</div>
				{#if result.recommended_actions?.length}
					<ul class="list-disc ml-5 space-y-0.5">
						{#each result.recommended_actions as bullet}
							<li>{bullet}</li>
						{/each}
					</ul>
				{:else}
					<div class="text-xs text-gray-500">{m.noData()}</div>
				{/if}
			</div>
			<div class="bg-white rounded-md p-3 border">
				<div class="font-semibold mb-1">{m.executiveSummary()}</div>
				<p class="whitespace-pre-wrap">{result.summary}</p>
			</div>
		</div>
	{:else}
		<div class="text-xs text-gray-600">
			{m.aiInsights()} — click "{m.generateInsights()}" to analyze your portfolio.
		</div>
	{/if}
</section>
