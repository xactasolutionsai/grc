<script lang="ts">
	import { getCoverageColor } from './api.js';
	import { goto } from '$app/navigation';

	interface CoverageCell {
		entity_type: string;
		entity_type_label: string;
		criticality: string;
		criticality_label: string;
		total: number;
		current: number;
		due_soon: number;
		overdue: number;
		never_audited: number;
	}

	interface Props {
		matrix?: CoverageCell[];
	}

	let { matrix = [] }: Props = $props();

	// Get unique entity types and criticality levels
	let entityTypes = $derived([...new Set(matrix.map(m => m.entity_type))]);
	let criticalityLevels = $derived(['High', 'Medium', 'Low']);

	// Create a map for quick lookup
	let matrixMap = $derived(
		matrix.reduce((acc: Record<string, CoverageCell>, item: CoverageCell) => {
			const key = `${item.entity_type}-${item.criticality}`;
			acc[key] = item;
			return acc;
		}, {})
	);

	// Get cell data for specific entity type and criticality
	function getCellData(entityType: string, criticality: string): CoverageCell | null {
		const key = `${entityType}-${criticality}`;
		return matrixMap[key] || null;
	}

	// Get tooltip text for a cell
	function getTooltip(cellData: CoverageCell | null): string {
		if (!cellData) return '';
		return `${cellData.entity_type_label} - ${cellData.criticality_label}\n` +
			   `Total: ${cellData.total}\n` +
			   `Current: ${cellData.current}\n` +
			   `Due Soon: ${cellData.due_soon}\n` +
			   `Overdue: ${cellData.overdue}\n` +
			   `Never Audited: ${cellData.never_audited}`;
	}

	// Navigate to universe page with filters
	function handleCellClick(entityType: string, criticality: string): void {
		const params = new URLSearchParams({
			entity_type: entityType,
			criticality: criticality
		});
		goto(`/audits/universe?${params.toString()}`);
	}
</script>

<div class="overflow-x-auto">
	<table class="w-full border-collapse shadow-sm">
		<thead>
			<tr class="bg-gradient-to-r from-surface-100 to-surface-50 dark:from-surface-800 dark:to-surface-900">
				<th class="p-4 text-left text-sm font-bold text-surface-800 dark:text-surface-200 border border-surface-300 dark:border-surface-600 sticky left-0 bg-surface-100 dark:bg-surface-800 z-10">
					<i class="fa-solid fa-layer-group mr-2 text-primary-600"></i>
					Entity Type / Criticality
				</th>
				{#each criticalityLevels as criticality}
					<th class="p-4 text-center text-sm font-bold text-surface-800 dark:text-surface-200 border border-surface-300 dark:border-surface-600 min-w-[120px]">
						<i class="fa-solid {criticality === 'High' ? 'fa-circle-exclamation text-error-500' : criticality === 'Medium' ? 'fa-circle-dot text-warning-500' : 'fa-circle text-success-500'} mr-1"></i>
						{criticality}
					</th>
				{/each}
			</tr>
		</thead>
		<tbody>
			{#each entityTypes as entityType}
				<tr class="hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors">
					<td class="p-4 text-sm font-semibold text-surface-700 dark:text-surface-300 border border-surface-300 dark:border-surface-600 bg-surface-50 dark:bg-surface-900/70 sticky left-0 z-10">
						{entityType.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
					</td>
					{#each criticalityLevels as criticality}
						{@const cellData = getCellData(entityType, criticality)}
						{@const color = cellData ? getCoverageColor(cellData.current, cellData.due_soon, cellData.overdue, cellData.never_audited) : '#f8fafc'}
						<td
							onclick={() => cellData && handleCellClick(entityType, criticality)}
							class="p-4 text-center border border-surface-300 dark:border-surface-600 cursor-pointer hover:scale-105 transition-all duration-200 hover:z-20 relative group"
							style="background-color: {color};"
							title={getTooltip(cellData)}
						>
							{#if cellData}
								<div class="text-white font-bold text-2xl drop-shadow-lg">
									{cellData.total}
								</div>
								<div class="text-xs font-medium text-white/95 mt-2 bg-black/20 rounded-full px-2 py-1 inline-block">
									{#if cellData.overdue > 0 || cellData.never_audited > 0}
										<i class="fa-solid fa-exclamation-triangle"></i> {cellData.overdue + cellData.never_audited} overdue
									{:else if cellData.due_soon > 0}
										<i class="fa-solid fa-clock"></i> {cellData.due_soon} due soon
									{:else}
										<i class="fa-solid fa-check-circle"></i> Current
									{/if}
								</div>
								<!-- Tooltip on hover -->
								<div class="absolute hidden group-hover:block left-1/2 -translate-x-1/2 bottom-full mb-2 p-3 bg-surface-900 dark:bg-surface-100 text-white dark:text-surface-900 text-xs rounded-lg shadow-xl z-30 whitespace-nowrap">
									<div class="font-bold mb-1">{cellData.entity_type_label} - {cellData.criticality_label}</div>
									<div class="space-y-0.5">
										<div>✓ Current: {cellData.current}</div>
										<div>⏰ Due Soon: {cellData.due_soon}</div>
										<div>⚠️ Overdue: {cellData.overdue}</div>
										<div>❌ Never Audited: {cellData.never_audited}</div>
									</div>
								</div>
							{:else}
								<div class="text-surface-400 dark:text-surface-500 text-lg font-medium">-</div>
							{/if}
						</td>
					{/each}
				</tr>
			{/each}
		</tbody>
	</table>

	<!-- Legend -->
	<div class="mt-6 p-4 bg-white dark:bg-surface-900 rounded-lg border border-surface-200 dark:border-surface-700">
		<div class="text-xs font-semibold text-surface-700 dark:text-surface-300 mb-3">
			<i class="fa-solid fa-info-circle mr-1"></i> Status Legend
		</div>
		<div class="flex flex-wrap gap-4 text-xs">
			<div class="flex items-center gap-2 px-3 py-2 bg-surface-50 dark:bg-surface-800 rounded-md">
				<div class="w-5 h-5 rounded shadow-sm" style="background-color: #10b981;"></div>
				<span class="font-medium text-surface-700 dark:text-surface-300">Current</span>
			</div>
			<div class="flex items-center gap-2 px-3 py-2 bg-surface-50 dark:bg-surface-800 rounded-md">
				<div class="w-5 h-5 rounded shadow-sm" style="background-color: #f59e0b;"></div>
				<span class="font-medium text-surface-700 dark:text-surface-300">Due Soon (80%+ of cycle)</span>
			</div>
			<div class="flex items-center gap-2 px-3 py-2 bg-surface-50 dark:bg-surface-800 rounded-md">
				<div class="w-5 h-5 rounded shadow-sm" style="background-color: #ef4444;"></div>
				<span class="font-medium text-surface-700 dark:text-surface-300">Overdue / Never Audited</span>
			</div>
			<div class="flex items-center gap-2 px-3 py-2 bg-surface-50 dark:bg-surface-800 rounded-md">
				<div class="w-5 h-5 rounded bg-surface-100 dark:bg-surface-700 border-2 border-surface-300 dark:border-surface-600"></div>
				<span class="font-medium text-surface-700 dark:text-surface-300">No Entities</span>
			</div>
		</div>
	</div>
</div>

