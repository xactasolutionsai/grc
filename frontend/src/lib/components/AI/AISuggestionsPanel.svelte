<script lang="ts">
	import type { AnalyzeRiskResult } from '$lib/utils/ai';
	import { m } from '$paraglide/messages';

	interface Props {
		result: AnalyzeRiskResult;
		onClose?: () => void;
	}

	let { result, onClose }: Props = $props();

	async function copyToClipboard(text: string) {
		try {
			await navigator.clipboard.writeText(text);
		} catch (_) {
			// clipboard may be unavailable; silently ignore
		}
	}
</script>

<div
	class="border border-primary-200 bg-primary-50 rounded-md p-3 text-sm space-y-3"
	data-testid="ai-suggestions-panel"
>
	<div class="flex items-center justify-between">
		<span class="font-semibold text-primary-900">{m.aiSuggestions()}</span>
		{#if onClose}
			<button
				type="button"
				class="text-xs text-primary-700 hover:underline"
				onclick={onClose}
			>
				×
			</button>
		{/if}
	</div>

	<div>
		<div class="font-medium">{m.threatScenario()}</div>
		<p class="text-gray-800 whitespace-pre-wrap">{result.threat_scenario}</p>
	</div>

	<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
		<div>
			<div class="font-medium">{m.riskLevel()}</div>
			<p class="text-gray-800">{result.risk_level}</p>
		</div>
		<div>
			<div class="font-medium">{m.likelihoodJustification()}</div>
			<p class="text-gray-800">
				{result.likelihood?.level ?? ''} — {result.likelihood?.justification ?? ''}
			</p>
		</div>
	</div>

	{#if result.recommended_mitigations?.length}
		<div>
			<div class="font-medium">{m.recommendedMitigations()}</div>
			<ul class="list-disc ml-5 space-y-1">
				{#each result.recommended_mitigations as mitigation}
					<li class="flex items-start justify-between gap-2">
						<span>{mitigation}</span>
						<button
							type="button"
							class="text-xs text-primary-700 hover:underline shrink-0"
							onclick={() => copyToClipboard(mitigation)}
						>
							copy
						</button>
					</li>
				{/each}
			</ul>
		</div>
	{/if}

	{#if result.security_domains?.length}
		<div>
			<div class="font-medium">{m.securityDomains()}</div>
			<div class="flex flex-wrap gap-1">
				{#each result.security_domains as domain}
					<span class="chip text-xs px-2 py-0.5 rounded-full bg-primary-100"
						>{domain}</span
					>
				{/each}
			</div>
		</div>
	{/if}
</div>
