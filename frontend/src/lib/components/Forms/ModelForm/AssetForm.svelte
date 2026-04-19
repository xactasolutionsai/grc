<script lang="ts">
	import { page } from '$app/state';
	import Dropdown from '$lib/components/Dropdown/Dropdown.svelte';
	import Checkbox from '$lib/components/Forms/Checkbox.svelte';
	import TextField from '$lib/components/Forms/TextField.svelte';
	import { SECURITY_OBJECTIVE_SCALE_MAP } from '$lib/utils/constants';

	import { safeTranslate } from '$lib/utils/i18n';
	import type { CacheLock, ModelInfo } from '$lib/utils/types';
	import { m } from '$paraglide/messages';
	import { onMount } from 'svelte';
	import type { SuperValidated } from 'sveltekit-superforms';
	import AutocompleteSelect from '../AutocompleteSelect.svelte';
	import Duration from '../Duration.svelte';
	import RadioGroup from '../RadioGroup.svelte';
	import Select from '../Select.svelte';
	import MarkdownField from '$lib/components/Forms/MarkdownField.svelte';
	import NumberField from '$lib/components/Forms/NumberField.svelte';
	import TextArea from '$lib/components/Forms/TextArea.svelte';

	interface Props {
		form: SuperValidated<any>;
		model: ModelInfo;
		cacheLocks?: Record<string, CacheLock>;
		formDataCache?: Record<string, any>;
		initialData?: Record<string, any>;
		object?: any;
		data?: any;
	}

	let {
		form,
		model,
		cacheLocks = {},
		formDataCache = $bindable({}),
		initialData = {},
		object = {},
		data = {}
	}: Props = $props();

	type SecurityObjectiveScale = '0-3' | '1-4' | 'FIPS-199';
	const scale: SecurityObjectiveScale = page.data.settings.security_objective_scale;
	const securityObjectiveScaleMap: string[] = SECURITY_OBJECTIVE_SCALE_MAP[scale];

	async function fetchSecurityObjectives(): Promise<string[]> {
		const endpoint = '/assets/security-objectives/';
		const objectives = await fetch(endpoint).then((res) => res.json());
		return objectives;
	}

	async function fetchDisasterRecoveryObjectives() {
		const endpoint = '/assets/disaster-recovery-objectives/';
		const objectives = await fetch(endpoint).then((res) => res.json());
		return objectives;
	}

	let securityObjectives: string[] = $state([]);
	let disasterRecoveryObjectives: string[] = $state([]);

	onMount(async () => {
		securityObjectives = await fetchSecurityObjectives();
		disasterRecoveryObjectives = await fetchDisasterRecoveryObjectives();
	});

	interface Option {
		label: string;
		value: number;
		suggested?: boolean;
	}

	const createOption = (label: string, value: number): Option => ({
		label,
		value
	});

	// Helper function to filter duplicate consecutive labels
	const filterDuplicateLabels = (options: Option[]): Option[] =>
		options.map((option, index, arr) => ({
			...option,
			label: index > 0 && option.label === arr[index - 1].label ? '' : option.label
		}));

	const securityObjectiveOptions: Option[] = filterDuplicateLabels(
		securityObjectiveScaleMap.map(createOption)
	);
</script>

<AutocompleteSelect
	{form}
	optionsEndpoint="asset-class"
	optionsLabelField="full_path"
	field="asset_class"
	cacheLock={cacheLocks['asset_class']}
	bind:cachedValue={formDataCache['asset_class']}
	label={m.assetClass()}
/>
<TextField
	{form}
	field="ref_id"
	cacheLock={cacheLocks['ref_id']}
	bind:cachedValue={formDataCache['ref_id']}
	label={m.refId()}
/>

<AutocompleteSelect
	{form}
	multiple
	optionsEndpoint="users?is_third_party=false"
	optionsLabelField="email"
	field="owner"
	cacheLock={cacheLocks['owner']}
	bind:cachedValue={formDataCache['owner']}
	label={m.owner()}
/>
<AutocompleteSelect
	{form}
	optionsEndpoint="folders?content_type=DO&content_type=GL"
	pathField="path"
	field="folder"
	cacheLock={cacheLocks['folder']}
	bind:cachedValue={formDataCache['folder']}
	label={m.domain()}
	hidden={initialData.folder}
/>
<Select
	{form}
	options={model.selectOptions['type']}
	disableDoubleDash={true}
	field="type"
	label="Type"
	cacheLock={cacheLocks['type']}
	bind:cachedValue={formDataCache['type']}
/>
<AutocompleteSelect
	disabled={data.type === 'PR'}
	hidden={data.type === 'PR'}
	multiple
	{form}
	optionsEndpoint="assets"
	optionsInfoFields={{
		fields: [
			{
				field: 'type'
			}
		],
		classes: 'text-blue-500'
	}}
	optionsDetailedUrlParameters={[['exclude_children', object.id]]}
	optionsLabelField="auto"
	pathField="path"
	optionsSelf={object}
	field="parent_assets"
	cacheLock={cacheLocks['parent_assets']}
	bind:cachedValue={formDataCache['parent_assets']}
	label={m.parentAssets()}
/>
<TextField
	{form}
	field="reference_link"
	label={m.link()}
	helpText={m.linkHelpText()}
	cacheLock={cacheLocks['reference_link']}
	bind:cachedValue={formDataCache['reference_link']}
/>
{#if data.type === 'PR'}
	<Dropdown
		open={false}
		style="hover:text-primary-700"
		icon="fa-solid fa-shield-halved"
		header={m.securityObjectives()}
	>
		<div class="flex flex-col space-y-4">
			{#each securityObjectives as objective}
				{@const objectiveFormData =
					data.security_objectives?.objectives &&
					Object.hasOwn(data.security_objectives?.objectives, objective)
						? data.security_objectives.objectives[objective]
						: {}}
				<span class="flex flex-row items-end space-x-4">
					<Checkbox
						{form}
						field={objective}
						label={''}
						valuePath="security_objectives.objectives.{objective}.is_enabled"
						checkboxComponent="switch"
						class="h-full flex flex-row items-center justify-center my-1"
						classesContainer="h-full"
					/>
					<RadioGroup
						possibleOptions={securityObjectiveOptions}
						{form}
						label={safeTranslate(objective)}
						labelKey="label"
						key="value"
						field={objective}
						valuePath="security_objectives.objectives.{objective}.value"
						disabled={objectiveFormData && objectiveFormData.is_enabled === false}
					/>
				</span>
			{/each}
		</div>
	</Dropdown>
	<Dropdown
		open={false}
		style="hover:text-indigo-700"
		icon="fa-regular fa-clock"
		header={m.disasterRecoveryObjectives()}
	>
		<div class="flex flex-col space-y-4">
			{#each disasterRecoveryObjectives as objective}
				<Duration
					{form}
					field={objective}
					label={safeTranslate(objective)}
					helpText={Object.hasOwn(m, `${objective}HelpText`) ? m[`${objective}HelpText`]() : ''}
					valuePath="disaster_recovery_objectives.objectives.{objective}.value"
				/>
			{/each}
		</div>
	</Dropdown>
{/if}
<AutocompleteSelect
	multiple
	{form}
	createFromSelection={true}
	optionsEndpoint="filtering-labels"
	optionsLabelField="label"
	field="filtering_labels"
	helpText={m.labelsHelpText()}
	label={m.labels()}
	translateOptions={false}
	allowUserOptions="append"
/>
<MarkdownField
	{form}
	field="observation"
	label={m.observation()}
	helpText={m.observationHelpText()}
	cacheLock={cacheLocks['observation']}
	bind:cachedValue={formDataCache['observation']}
/>
{#if initialData.ebios_rm_studies}
	<AutocompleteSelect
		{form}
		field="ebios_rm_studies"
		multiple
		cacheLock={cacheLocks['ebios_rm_studies']}
		bind:cachedValue={formDataCache['ebios_rm_studies']}
		label={m.ebiosRmStudies()}
		hidden
	/>
{/if}

<!-- ITAM (IT Asset Management) Fields -->
<div class="space-y-8">
	<!-- Inventory Section -->
	<Dropdown
		open={false}
		style="hover:text-blue-700"
		icon="fa-solid fa-box"
		header={m.inventory()}
	>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<Select
				{form}
				options={[
					{ label: 'Hardware', value: 'hardware' },
					{ label: 'Software', value: 'software' },
					{ label: 'Cloud', value: 'cloud' },
					{ label: 'Digital', value: 'digital' }
				]}
				field="asset_type"
				label={m.assetType()}
				cacheLock={cacheLocks['asset_type']}
				bind:cachedValue={formDataCache['asset_type']}
			/>
			<TextField
				{form}
				field="serial_number"
				label={m.serialNumber()}
				cacheLock={cacheLocks['serial_number']}
				bind:cachedValue={formDataCache['serial_number']}
			/>
			<TextArea
				{form}
				field="specifications"
				label={m.specifications()}
				cacheLock={cacheLocks['specifications']}
				bind:cachedValue={formDataCache['specifications']}
			/>
			<TextField
				{form}
				field="license_key"
				label={m.licenseKey()}
				cacheLock={cacheLocks['license_key']}
				bind:cachedValue={formDataCache['license_key']}
			/>
		</div>
	</Dropdown>

	<!-- Ownership & Location Section -->
	<Dropdown
		open={false}
		style="hover:text-green-700"
		icon="fa-solid fa-user-location"
		header={m.ownershipLocation()}
	>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<TextField
				{form}
				field="assigned_user"
				label={m.assignedUser()}
				cacheLock={cacheLocks['assigned_user']}
				bind:cachedValue={formDataCache['assigned_user']}
			/>
			<TextField
				{form}
				field="department"
				label={m.department()}
				cacheLock={cacheLocks['department']}
				bind:cachedValue={formDataCache['department']}
			/>
			<TextField
				{form}
				field="physical_location"
				label={m.physicalLocation()}
				cacheLock={cacheLocks['physical_location']}
				bind:cachedValue={formDataCache['physical_location']}
			/>
			<TextField
				{form}
				field="virtual_location"
				label={m.virtualLocation()}
				cacheLock={cacheLocks['virtual_location']}
				bind:cachedValue={formDataCache['virtual_location']}
			/>
		</div>
	</Dropdown>

	<!-- Lifecycle Section -->
	<Dropdown
		open={false}
		style="hover:text-purple-700"
		icon="fa-solid fa-clock"
		header={m.lifecycle()}
	>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<TextField
				{form}
				field="acquisition_date"
				label={m.acquisitionDate()}
				type="date"
				cacheLock={cacheLocks['acquisition_date']}
				bind:cachedValue={formDataCache['acquisition_date']}
			/>
			<TextField
				{form}
				field="end_of_life_date"
				label={m.endOfLifeDate()}
				type="date"
				cacheLock={cacheLocks['end_of_life_date']}
				bind:cachedValue={formDataCache['end_of_life_date']}
			/>
			<TextArea
				{form}
				field="deployment_details"
				label={m.deploymentDetails()}
				cacheLock={cacheLocks['deployment_details']}
				bind:cachedValue={formDataCache['deployment_details']}
			/>
			<TextArea
				{form}
				field="maintenance_schedule"
				label={m.maintenanceSchedule()}
				cacheLock={cacheLocks['maintenance_schedule']}
				bind:cachedValue={formDataCache['maintenance_schedule']}
			/>
			<TextArea
				{form}
				field="upgrade_history"
				label={m.upgradeHistory()}
				helpText={'JSON format: [{"version": "1.0", "date": "2024-01-15", "description": "Initial installation"}]'}
				cacheLock={cacheLocks['upgrade_history']}
				bind:cachedValue={formDataCache['upgrade_history']}
			/>
		</div>
	</Dropdown>

	<!-- Licensing & Compliance Section -->
	<Dropdown
		open={false}
		style="hover:text-yellow-700"
		icon="fa-solid fa-certificate"
		header={m.licensingCompliance()}
	>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<TextField
				{form}
				field="license_number"
				label={m.licenseNumber()}
				cacheLock={cacheLocks['license_number']}
				bind:cachedValue={formDataCache['license_number']}
			/>
			<TextField
				{form}
				field="license_type"
				label={m.licenseType()}
				cacheLock={cacheLocks['license_type']}
				bind:cachedValue={formDataCache['license_type']}
			/>
			<TextField
				{form}
				field="license_expiry_date"
				label={m.licenseExpiryDate()}
				type="date"
				cacheLock={cacheLocks['license_expiry_date']}
				bind:cachedValue={formDataCache['license_expiry_date']}
			/>
			<TextField
				{form}
				field="compliance_status"
				label={m.complianceStatus()}
				cacheLock={cacheLocks['compliance_status']}
				bind:cachedValue={formDataCache['compliance_status']}
			/>
			<TextArea
				{form}
				field="audit_logs"
				label={m.auditLogs()}
				helpText={'JSON format: [{"date": "2024-01-15", "action": "Created", "user": "admin"}]'}
				cacheLock={cacheLocks['audit_logs']}
				bind:cachedValue={formDataCache['audit_logs']}
			/>
		</div>
	</Dropdown>

	<!-- Financials Section -->
	<Dropdown
		open={false}
		style="hover:text-green-600"
		icon="fa-solid fa-dollar-sign"
		header={m.financials()}
	>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<NumberField
				{form}
				field="purchase_cost"
				label={m.purchaseCost()}
				step="0.01"
				cacheLock={cacheLocks['purchase_cost']}
				bind:cachedValue={formDataCache['purchase_cost']}
			/>
			<NumberField
				{form}
				field="depreciation_value"
				label={m.depreciationValue()}
				step="0.01"
				cacheLock={cacheLocks['depreciation_value']}
				bind:cachedValue={formDataCache['depreciation_value']}
			/>
			<NumberField
				{form}
				field="total_cost_of_ownership"
				label={m.totalCostOfOwnership()}
				step="0.01"
				cacheLock={cacheLocks['total_cost_of_ownership']}
				bind:cachedValue={formDataCache['total_cost_of_ownership']}
			/>
			<TextField
				{form}
				field="vendor"
				label={m.vendor()}
				cacheLock={cacheLocks['vendor']}
				bind:cachedValue={formDataCache['vendor']}
			/>
			<TextArea
				{form}
				field="warranty"
				label={m.warranty()}
				cacheLock={cacheLocks['warranty']}
				bind:cachedValue={formDataCache['warranty']}
			/>
		</div>
	</Dropdown>

	<!-- Operations Section -->
	<Dropdown
		open={false}
		style="hover:text-orange-700"
		icon="fa-solid fa-cogs"
		header={m.operations()}
	>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<TextArea
				{form}
				field="service_history"
				label={m.serviceHistory()}
				helpText={'JSON format: [{"date": "2024-01-15", "type": "maintenance", "description": "Routine check"}]'}
				cacheLock={cacheLocks['service_history']}
				bind:cachedValue={formDataCache['service_history']}
			/>
			<TextArea
				{form}
				field="preventive_maintenance"
				label={m.preventiveMaintenance()}
				cacheLock={cacheLocks['preventive_maintenance']}
				bind:cachedValue={formDataCache['preventive_maintenance']}
			/>
			<TextArea
				{form}
				field="sla_details"
				label={m.slaDetails()}
				cacheLock={cacheLocks['sla_details']}
				bind:cachedValue={formDataCache['sla_details']}
			/>
			<TextArea
				{form}
				field="spare_parts"
				label={m.spareParts()}
				cacheLock={cacheLocks['spare_parts']}
				bind:cachedValue={formDataCache['spare_parts']}
			/>
		</div>
	</Dropdown>

	<!-- Security & Risk Section -->
	<Dropdown
		open={false}
		style="hover:text-red-700"
		icon="fa-solid fa-shield-halved"
		header={m.securityRisk()}
	>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<TextArea
				{form}
				field="security_config"
				label={m.securityConfig()}
				helpText={'JSON format: {"encryption": true, "firewall": "enabled"}'}
				cacheLock={cacheLocks['security_config']}
				bind:cachedValue={formDataCache['security_config']}
			/>
			<TextArea
				{form}
				field="known_vulnerabilities"
				label={m.knownVulnerabilities()}
				helpText={'JSON format: [{"cve": "CVE-2024-001", "severity": "high"}]'}
				cacheLock={cacheLocks['known_vulnerabilities']}
				bind:cachedValue={formDataCache['known_vulnerabilities']}
			/>
			<TextArea
				{form}
				field="incident_records"
				label={m.incidentRecords()}
				helpText={'JSON format: [{"date": "2024-01-15", "severity": "high", "description": "Security incident"}]'}
				cacheLock={cacheLocks['incident_records']}
				bind:cachedValue={formDataCache['incident_records']}
			/>
			<TextArea
				{form}
				field="compliance_standards"
				label={m.complianceStandards()}
				helpText={'JSON format: ["ISO27001", "SOC2"]'}
				cacheLock={cacheLocks['compliance_standards']}
				bind:cachedValue={formDataCache['compliance_standards']}
			/>
		</div>
	</Dropdown>
</div>
