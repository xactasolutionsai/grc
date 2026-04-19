<script lang="ts">
	import { run } from 'svelte/legacy';

	import type { RiskMatrixJsonDefinition } from '$lib/utils/types';
	import Selector from './selector.svelte';
	import { average, forms } from './utils';
	import { m } from '$paraglide/messages';
	import { ChevronRight, ChevronLeft } from 'lucide-svelte';

	let { data, risk_matrices = data.risk_matrices } = $props();

	let risk_matrix_index = $state(0);
	let risk_matrix_select: Element = $state();
	let risk_matrix: RiskMatrixJsonDefinition = $derived(risk_matrices[risk_matrix_index] ?? null);
	let is_business_impact_ignored = $state(false);

	let vector: number[] = $state();
	let vector_string: string = $state();
	let form_data = $state({
		threat_agent: [0, 0, 0, 0],
		business_impact: [0, 0, 0, 0],
		vulnerability: [0, 0, 0, 0],
		technical_impact: [0, 0, 0, 0]
	});

	let threat_agent_score = $derived(average(form_data.threat_agent));
	let business_impact_score = $derived(average(form_data.business_impact));
	let vulnerability_score = $derived(average(form_data.vulnerability));
	let technical_impact_score = $derived(average(form_data.technical_impact));

	let impact_score = $derived(
		is_business_impact_ignored ? technical_impact_score : business_impact_score
	);
	let probability_score = $derived(average([threat_agent_score, vulnerability_score]));
	let risk_score = $derived(average([impact_score, probability_score]));

	run(() => {
		vector = [
			...form_data.threat_agent,
			...form_data.business_impact,
			...form_data.vulnerability,
			...form_data.technical_impact
		];
	});

	run(() => {
		let strings: string[] = [];
		for (let i = 0; i < 4; i++) {
			strings.push(vector.slice(4 * i, 4 * (i + 1)).join(''));
		}
		vector_string = strings.join('-');
	});

	function update_scores(risk_score: number, risk_matrix: RiskMatrixJsonDefinition) {
		if (!risk_matrix) return;
		const probabilityPartitionSize = 10 / risk_matrix['probability'].length;
		const impactPartitionSize = 10 / risk_matrix['impact'].length;
		const riskPartitionSize = 10 / risk_matrix['risk'].length;

		const probability_index = Math.floor(probability_score / probabilityPartitionSize);
		const impact_index = Math.floor(impact_score / impactPartitionSize);
		const risk_index = Math.floor(risk_score / riskPartitionSize);

		return {
			probability: risk_matrix.probability[probability_index],
			impact: risk_matrix.impact[impact_index],
			risk: risk_matrix.risk[risk_index]
		};
	}

	let labels = $derived(update_scores(risk_score, risk_matrix));
</script>

<main class="h-full flex flex-col">
	{#if risk_matrix}
		<div class="max-w-7xl mx-auto w-full p-6 space-y-5">
			<!-- Matrix selector bar -->
			<div class="flex items-center gap-3 bg-white border border-surface-200 rounded-lg px-4 py-3">
				<span class="text-sm font-medium text-surface-500">{m.riskMatrix()}</span>
				<select
					id="risk-matrix-select"
					class="select form-input text-sm border border-surface-300 rounded-md px-3 py-1.5 w-auto"
					bind:value={risk_matrix_index}
					bind:this={risk_matrix_select}
				>
					{#each risk_matrices as rm, index}
						<option value={index}>{rm.name}</option>
					{/each}
				</select>
			</div>

			<!-- Two-column scoring grid -->
			<div class="grid lg:grid-cols-2 gap-5">
				<!-- LEFT: Likelihood -->
				<div class="space-y-4">
					<div class="text-[11px] font-bold uppercase tracking-widest text-surface-400 px-1">{m.probability()}</div>

					<!-- Threat Agent Factors -->
					<div id="ta_div" class="bg-white border border-surface-200 rounded-lg overflow-hidden">
						<div class="flex items-center justify-between bg-surface-50 border-b border-surface-200 px-4 py-2.5">
							<span class="text-sm font-semibold text-surface-700">{m.threatAgentFactors()}</span>
							<span class="bg-primary-500 text-white text-xs font-bold rounded-full px-3 py-0.5 min-w-[36px] text-center" id="threat_agent_score">
								{threat_agent_score}
							</span>
						</div>
						<div class="p-4 space-y-2.5">
							{#each forms.threat_agent as selector_data, index}
								<Selector
									{...selector_data}
									on:change={(e) => {
										form_data.threat_agent[index] = e.detail;
									}}
								/>
							{/each}
						</div>
					</div>

					<!-- Vulnerability Factors -->
					<div id="vf_div" class="bg-white border border-surface-200 rounded-lg overflow-hidden">
						<div class="flex items-center justify-between bg-surface-50 border-b border-surface-200 px-4 py-2.5">
							<span class="text-sm font-semibold text-surface-700">{m.vulnerabilityFactors()}</span>
							<span class="bg-primary-500 text-white text-xs font-bold rounded-full px-3 py-0.5 min-w-[36px] text-center" id="vulnerability_score">
								{vulnerability_score}
							</span>
						</div>
						<div class="p-4 space-y-2.5">
							{#each forms.vulnerability as selector_data, index}
								<Selector
									{...selector_data}
									on:change={(e) => {
										form_data.vulnerability[index] = e.detail;
									}}
								/>
							{/each}
						</div>
					</div>
				</div>

				<!-- RIGHT: Impact -->
				<div class="space-y-4">
					<div class="text-[11px] font-bold uppercase tracking-widest text-surface-400 px-1">{m.impact()}</div>

					<!-- Business Impact Factors -->
					<div id="bi_div" class="border rounded-lg overflow-hidden transition-colors {is_business_impact_ignored ? 'bg-surface-50 border-surface-100' : 'bg-white border-surface-200'}">
						<div class="flex items-center justify-between border-b px-4 py-2.5 {is_business_impact_ignored ? 'bg-surface-100 border-surface-100' : 'bg-surface-50 border-surface-200'}">
							<span class="text-sm font-semibold {is_business_impact_ignored ? 'text-surface-400' : 'text-surface-700'}">{m.businessImpactFactors()}</span>
							<div class="flex items-center gap-3">
								<label class="flex items-center gap-1.5 cursor-pointer">
									<input
										id="ignore_business_impact"
										type="checkbox"
										class="w-3.5 h-3.5 rounded border-surface-300 accent-primary-500"
										bind:checked={is_business_impact_ignored}
									/>
									<span class="text-xs text-surface-500">{m.ignore()}</span>
								</label>
								<span class="text-white text-xs font-bold rounded-full px-3 py-0.5 min-w-[36px] text-center {is_business_impact_ignored ? 'bg-surface-300' : 'bg-primary-500'}" id="business_impact_score">
									{is_business_impact_ignored ? '--' : business_impact_score}
								</span>
							</div>
						</div>
						<div class="p-4 space-y-2.5 {is_business_impact_ignored ? 'opacity-50 pointer-events-none' : ''}">
							{#each forms.business_impact as selector_data, index}
								<Selector
									{...selector_data}
									disabled={is_business_impact_ignored}
									on:change={(e) => {
										form_data.business_impact[index] = e.detail;
									}}
								/>
							{/each}
						</div>
					</div>

					<!-- Technical Impact Factors -->
					<div id="ti_div" class="border rounded-lg overflow-hidden transition-colors {is_business_impact_ignored ? 'bg-white border-surface-200' : 'bg-surface-50 border-surface-100'}">
						<div class="flex items-center justify-between border-b px-4 py-2.5 {is_business_impact_ignored ? 'bg-surface-50 border-surface-200' : 'bg-surface-100 border-surface-100'}">
							<span class="text-sm font-semibold {is_business_impact_ignored ? 'text-surface-700' : 'text-surface-400'}">{m.technicalImpactFactors()}</span>
							<span class="text-white text-xs font-bold rounded-full px-3 py-0.5 min-w-[36px] text-center {is_business_impact_ignored ? 'bg-primary-500' : 'bg-surface-300'}" id="technical_impact_score">
								{is_business_impact_ignored ? technical_impact_score : '--'}
							</span>
						</div>
						<div class="p-4 space-y-2.5 {is_business_impact_ignored ? '' : 'opacity-50 pointer-events-none'}">
							{#each forms.technical_impact as selector_data, index}
								<Selector
									{...selector_data}
									disabled={!is_business_impact_ignored}
									on:change={(e) => {
										form_data.technical_impact[index] = e.detail;
									}}
								/>
							{/each}
						</div>
					</div>
				</div>
			</div>

			<!-- Results section -->
			<div class="bg-white border border-surface-200 rounded-lg overflow-hidden">
				<div class="px-5 py-3 bg-surface-50 border-b border-surface-200">
					<span class="font-mono text-xs text-surface-500">
						{m.assessmentVector()}:
						<span id="vector" class="bg-surface-200 rounded px-2 py-0.5 text-surface-700 font-semibold ml-1">{vector_string}</span>
					</span>
				</div>

				<div class="p-5">
					<div class="grid grid-cols-[1fr_auto_1fr] items-center gap-4">
						<!-- Probability -->
						<div class="border-l-4 border-l-primary-500 bg-surface-50 rounded-r-lg p-4">
							<div class="text-[11px] font-bold uppercase tracking-widest text-surface-400">{m.probability()}</div>
							<div class="text-xl font-bold text-surface-800 mt-1" id="probability_label">
								{labels.probability.name}
							</div>
							<div class="text-sm text-surface-500 mt-0.5">
								{probability_score === 0 ? '--' : probability_score}
							</div>
						</div>

						<!-- Risk Level -->
						<div class="flex flex-col items-center gap-2 px-2" id="score">
							<div class="text-[11px] font-bold uppercase tracking-widest text-surface-400">{m.riskLevel()}</div>
							<div class="flex items-center gap-2">
								<ChevronRight size={18} class="text-surface-300" />
								<span
									class="px-6 py-3 text-center font-bold text-xl rounded-lg shadow-md min-w-[120px]"
									id="risk_label"
									style="background-color: {labels.risk.hexcolor}"
								>
									{labels.risk.name}
								</span>
								<ChevronLeft size={18} class="text-surface-300" />
							</div>
						</div>

						<!-- Impact -->
						<div class="border-l-4 border-l-secondary-500 bg-surface-50 rounded-r-lg p-4">
							<div class="text-[11px] font-bold uppercase tracking-widest text-surface-400">{m.impact()}</div>
							<div class="text-xl font-bold text-surface-800 mt-1" id="impact_label">
								{labels.impact.name}
							</div>
							<div class="text-sm text-surface-500 mt-0.5">
								{impact_score === 0 ? '--' : impact_score}
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	{:else}
		<div class="flex items-center justify-center h-full">
			<div class="text-xl font-semibold text-surface-400">
				{m.scoringAssistantNoMatrixError()}
			</div>
		</div>
	{/if}
</main>
