<script lang="ts">
	import type { PageData } from './$types';
	import { m } from '$paraglide/messages';
	import ModelTable from '$lib/components/ModelTable/ModelTable.svelte';
	import ActivityTracker from '$lib/components/DataViz/ActivityTracker.svelte';
	import {
		Shield,
		CheckSquare,
		ClipboardCheck,
		BarChart3,
		AlertTriangle,
		Siren,
		ShieldOff,
		Search,
		Flag
	} from 'lucide-svelte';

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();
</script>

<div class="grid grid-cols-12 gap-5 p-4">
	<div class="col-span-12 lg:col-span-6 bg-white border border-surface-200 border-l-4 border-l-primary-400 rounded-lg shadow-sm p-4">
		<div class="flex items-center gap-2 mb-3">
			<Shield size={16} class="text-primary-500" />
			<span class="text-sm font-semibold uppercase tracking-wide text-surface-700">{m.appliedControls()}</span>
		</div>
		<ModelTable
			source={{
				head: {
					ref_id: 'ref_id',
					name: 'name',
					status: 'status',
					priority: 'priority',
					eta: 'eta',
					folder: 'folder'
				},
				body: []
			}}
			hideFilters={true}
			URLModel="applied-controls"
			baseEndpoint="/applied-controls?owner={data.user.id}"
		/>
	</div>
	<div class="col-span-12 lg:col-span-6 flex items-center justify-center p-4">
		<ActivityTracker metrics={data.data.metrics} />
	</div>

	<div class="col-span-12 lg:col-span-6 bg-white border border-surface-200 border-l-4 border-l-secondary-400 rounded-lg shadow-sm p-4">
		<div class="flex items-center gap-2 mb-3">
			<CheckSquare size={16} class="text-secondary-500" />
			<span class="text-sm font-semibold uppercase tracking-wide text-surface-700">{m.tasks()}</span>
		</div>
		<ModelTable
			source={{
				head: {
					name: 'name',
					status: 'status',
					is_recurrent: 'is_recurrent',
					next_occurrence: 'next_occurrence'
				},
				body: []
			}}
			hideFilters={true}
			URLModel="task-templates"
			baseEndpoint="/task-templates?assigned_to={data.user.id}"
		/>
	</div>
	<div class="col-span-12 lg:col-span-6 bg-white border border-surface-200 border-l-4 border-l-primary-400 rounded-lg shadow-sm p-4">
		<div class="flex items-center gap-2 mb-3">
			<ClipboardCheck size={16} class="text-primary-500" />
			<span class="text-sm font-semibold uppercase tracking-wide text-surface-700">{m.complianceAssessments()}</span>
		</div>
		<ModelTable
			source={{
				head: {
					name: 'name',
					status: 'status',
					eta: 'eta',
					progress: 'progress',
					perimeter: 'perimeter'
				},
				body: []
			}}
			hideFilters={true}
			URLModel="compliance-assessments"
			baseEndpoint="/compliance-assessments?authors={data.user.id}"
		/>
	</div>

	<div class="col-span-12 lg:col-span-6 bg-white border border-surface-200 border-l-4 border-l-tertiary-400 rounded-lg shadow-sm p-4">
		<div class="flex items-center gap-2 mb-3">
			<BarChart3 size={16} class="text-tertiary-500" />
			<span class="text-sm font-semibold uppercase tracking-wide text-surface-700">{m.riskAssessments()}</span>
		</div>
		<ModelTable
			source={{
				head: {
					name: 'name',
					status: 'status',
					eta: 'eta',
					perimeter: 'perimeter'
				},
				body: []
			}}
			hideFilters={true}
			URLModel="risk-assessments"
			baseEndpoint="/risk-assessments?authors={data.user.id}"
		/>
	</div>
	<div class="col-span-12 lg:col-span-6 bg-white border border-surface-200 border-l-4 border-l-tertiary-400 rounded-lg shadow-sm p-4">
		<div class="flex items-center gap-2 mb-3">
			<AlertTriangle size={16} class="text-tertiary-500" />
			<span class="text-sm font-semibold uppercase tracking-wide text-surface-700">{m.riskScenarios()}</span>
		</div>
		<ModelTable
			source={{
				head: {
					ref_id: 'ref_id',
					name: 'name',
					current_level: 'current_level',
					residual_level: 'residual_level',
					risk_assessment: 'risk_assessment'
				},
				body: []
			}}
			hideFilters={true}
			URLModel="risk-scenarios"
			baseEndpoint="/risk-scenarios?owner={data.user.id}"
		/>
	</div>

	<div class="col-span-12 lg:col-span-6 bg-white border border-surface-200 border-l-4 border-l-error-400 rounded-lg shadow-sm p-4">
		<div class="flex items-center gap-2 mb-3">
			<Siren size={16} class="text-error-500" />
			<span class="text-sm font-semibold uppercase tracking-wide text-surface-700">{m.incidents()}</span>
		</div>
		<ModelTable
			source={{
				head: {
					ref_id: 'ref_id',
					name: 'name',
					status: 'status',
					severity: 'severity',
					folder: 'folder'
				},
				body: []
			}}
			hideFilters={true}
			URLModel="incidents"
			baseEndpoint="/incidents?owners={data.user.id}"
		/>
	</div>
	<div class="col-span-12 lg:col-span-6 bg-white border border-surface-200 border-l-4 border-l-warning-400 rounded-lg shadow-sm p-4">
		<div class="flex items-center gap-2 mb-3">
			<ShieldOff size={16} class="text-warning-500" />
			<span class="text-sm font-semibold uppercase tracking-wide text-surface-700">{m.securityExceptions()}</span>
		</div>
		<ModelTable
			source={{
				head: {
					name: 'name',
					status: 'status',
					severity: 'severity',
					expiration_date: 'expiration_date',
					folder: 'folder'
				},
				body: []
			}}
			hideFilters={true}
			URLModel="security-exceptions"
			baseEndpoint="/security-exceptions?owners={data.user.id}"
		/>
	</div>

	<div class="col-span-12 lg:col-span-6 bg-white border border-surface-200 border-l-4 border-l-secondary-400 rounded-lg shadow-sm p-4">
		<div class="flex items-center gap-2 mb-3">
			<Search size={16} class="text-secondary-500" />
			<span class="text-sm font-semibold uppercase tracking-wide text-surface-700">{m.findingsAssessments()}</span>
		</div>
		<ModelTable
			source={{
				head: {
					name: 'name',
					status: 'status',
					category: 'category',
					perimeter: 'perimeter'
				},
				body: []
			}}
			hideFilters={true}
			URLModel="findings-assessments"
			baseEndpoint="/findings-assessments?authors={data.user.id}"
		/>
	</div>
	<div class="col-span-12 lg:col-span-6 bg-white border border-surface-200 border-l-4 border-l-error-400 rounded-lg shadow-sm p-4">
		<div class="flex items-center gap-2 mb-3">
			<Flag size={16} class="text-error-500" />
			<span class="text-sm font-semibold uppercase tracking-wide text-surface-700">{m.findings()}</span>
		</div>
		<ModelTable
			source={{
				head: {
					ref_id: 'ref_id',
					name: 'name',
					severity: 'severity',
					status: 'status'
				},
				body: []
			}}
			hideFilters={true}
			URLModel="findings"
			baseEndpoint="/findings?owner={data.user.id}"
		/>
	</div>
</div>
