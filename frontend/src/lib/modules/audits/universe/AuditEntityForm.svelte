<script lang="ts">
	import { onMount } from 'svelte';
	import { createEntity, listEntities } from './api.js';
	import { uploadOrgStructure } from './api.js';
	import { getUsers } from './users-api.js';
	import FormSection from './FormSection.svelte';

	export let onSaved = () => {};

	let form = {
		name: '',
		entity_type: 'process',
		description: '',
		objectives: '',
		parent: null as string | null,
		owner: null as string | null,
		team_member: null as string | null,
		contact_type: 'owner',
		key_contact: null as string | null,
		risk_score: 0,
		inherent_risk_score: null as number | null,
		residual_risk_score: null as number | null,
		control_maturity: null as number | null,
		regulatory_relevance: '',
		last_audited: '',
		criticality: 'Medium',
		priority: 'medium',
		audit_frequency: 'annual',
		next_audit_date: '',
		location: '',
		country: '',
		region: '',
		city: '',
		address: '',
		postal_code: '',
		timezone: '',
		coordinates: null as { latitude: number; longitude: number } | null,
		notes: '',
		is_active: true
	};

	let saving = false;
	let error: string | null = null;
	let entities: any[] = [];
	let users: any[] = []; // This would need to be fetched from a users API
	let orgStructureFile: File | null = null;

	const entityTypes = [
		{ value: 'business_unit', label: 'Business Unit' },
		{ value: 'division', label: 'Division' },
		{ value: 'function', label: 'Function' },
		{ value: 'section', label: 'Section' },
		{ value: 'unit', label: 'Unit' },
		{ value: 'process', label: 'Process' },
		{ value: 'system', label: 'System' },
		{ value: 'vendor', label: 'Vendor' },
		{ value: 'compliance_domain', label: 'Compliance Domain' },
		{ value: 'audit_domain', label: 'Audit Domain' }
	];

	const criticalityChoices = [
		{ value: 'High', label: 'High' },
		{ value: 'Medium', label: 'Medium' },
		{ value: 'Low', label: 'Low' }
	];

	const priorityChoices = [
		{ value: 'low', label: 'Low' },
		{ value: 'medium', label: 'Medium' },
		{ value: 'high', label: 'High' },
		{ value: 'critical', label: 'Critical' }
	];

	const auditFrequencyChoices = [
		{ value: 'annual', label: 'Annual' },
		{ value: 'semiannual', label: 'Semi-annual' },
		{ value: 'quarterly', label: 'Quarterly' },
		{ value: 'monthly', label: 'Monthly' },
		{ value: 'ad-hoc', label: 'Ad-hoc' }
	];

	const commonTimezones = [
		{ value: '', label: 'Select timezone (optional)' },
		{ value: 'UTC', label: 'UTC' },
		{ value: 'America/New_York', label: 'America/New_York (EST/EDT)' },
		{ value: 'America/Chicago', label: 'America/Chicago (CST/CDT)' },
		{ value: 'America/Denver', label: 'America/Denver (MST/MDT)' },
		{ value: 'America/Los_Angeles', label: 'America/Los_Angeles (PST/PDT)' },
		{ value: 'Europe/London', label: 'Europe/London (GMT/BST)' },
		{ value: 'Europe/Paris', label: 'Europe/Paris (CET/CEST)' },
		{ value: 'Europe/Berlin', label: 'Europe/Berlin (CET/CEST)' },
		{ value: 'Asia/Tokyo', label: 'Asia/Tokyo (JST)' },
		{ value: 'Asia/Shanghai', label: 'Asia/Shanghai (CST)' },
		{ value: 'Asia/Kolkata', label: 'Asia/Kolkata (IST)' },
		{ value: 'Australia/Sydney', label: 'Australia/Sydney (AEST/AEDT)' },
		{ value: 'Pacific/Auckland', label: 'Pacific/Auckland (NZST/NZDT)' }
	];

	onMount(async () => {
		// Load existing entities for parent dropdown
		try {
			const data = await listEntities();
			entities = data.results || data;
		} catch (err: any) {
			console.error('Error loading entities for parent dropdown:', err);
		}

		// Load users for owner dropdowns
		try {
			const data = await getUsers();
			users = data.results || data;
		} catch (err: any) {
			console.error('Error loading users for owner dropdowns:', err);
		}
	});

	function formatEntityType(type: string) {
		return type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
	}

	function handleChange(event: any) {
		const { name, value, type, checked } = event.target;
		form = {
			...form,
			[name]: type === 'checkbox' ? checked : value
		};
	}

	function handleRegulatoryRelevanceChange(event: any) {
		const value = event.target.value;
		try {
			// Try to parse as JSON if it looks like JSON
			if (value.trim().startsWith('{') || value.trim().startsWith('[')) {
				form.regulatory_relevance = JSON.parse(value);
			} else {
				form.regulatory_relevance = value;
			}
		} catch {
			// If not valid JSON, store as string
			form.regulatory_relevance = value;
		}
	}

	function handleCoordinateChange(lat: string, lng: string) {
		const latitude = parseFloat(lat);
		const longitude = parseFloat(lng);

		if (!isNaN(latitude) && !isNaN(longitude)) {
			form.coordinates = { latitude, longitude };
		} else {
			form.coordinates = null;
		}
	}

	function clearCoordinates() {
		form.coordinates = null;
	}

	async function handleSubmit(event: any) {
		event.preventDefault();
		saving = true;
		error = null;

		try {
			// Clean up form data - convert empty strings to null or delete
			const formData: any = { ...form };

			// Convert empty strings to null for optional fields
			if (!formData.last_audited || formData.last_audited === '') delete formData.last_audited;
			if (!formData.next_audit_date || formData.next_audit_date === '') delete formData.next_audit_date;
			if (!formData.parent || formData.parent === '' || formData.parent === 'null') formData.parent = null;
			if (!formData.owner || formData.owner === '' || formData.owner === 'null') formData.owner = null;
			if (!formData.team_member || formData.team_member === '' || formData.team_member === 'null') formData.team_member = null;
			if (!formData.key_contact || formData.key_contact === '' || formData.key_contact === 'null') formData.key_contact = null;
			if (!formData.regulatory_relevance || formData.regulatory_relevance === '') delete formData.regulatory_relevance;

			// Convert numeric fields
			if (formData.inherent_risk_score === '' || formData.inherent_risk_score === null) delete formData.inherent_risk_score;
			if (formData.residual_risk_score === '' || formData.residual_risk_score === null) delete formData.residual_risk_score;
			if (formData.control_maturity === '' || formData.control_maturity === null) delete formData.control_maturity;

			// is_active is always included as it has a default value

			console.log('Submitting entity data:', formData);
			const created = await createEntity(formData);
			if (orgStructureFile) {
				try {
					await uploadOrgStructure(created.id, orgStructureFile);
				} catch (err) {
					console.error('Org structure upload failed (continuing):', err);
				}
			}
			onSaved();

			// Reset form
			form = {
				name: '',
				entity_type: 'process',
				description: '',
				objectives: '',
				parent: null,
				owner: null,
				team_member: null,
				contact_type: 'owner',
				key_contact: null,
				risk_score: 0,
				inherent_risk_score: null,
				residual_risk_score: null,
				control_maturity: null,
				regulatory_relevance: '',
				last_audited: '',
				criticality: 'Medium',
				priority: 'medium',
				audit_frequency: 'annual',
				next_audit_date: '',
				location: '',
				country: '',
				region: '',
				city: '',
				address: '',
				postal_code: '',
				timezone: '',
				coordinates: null,
				notes: '',
				is_active: true
			};
			orgStructureFile = null;
		} catch (err: any) {
			console.error('Error creating entity:', err);
			error = err.message;
		} finally {
			saving = false;
		}
	}
</script>

<div class="enhanced-modal-body">
	{#if error}
		<div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-lg p-4 mb-4 flex items-start gap-3">
			<svg class="h-5 w-5 text-error-600 dark:text-error-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<div class="text-error-800 dark:text-error-200 text-sm">{error}</div>
		</div>
	{/if}

	<form on:submit={handleSubmit} class="space-y-4">
		<!-- Basic Information Section -->
		<FormSection title="Basic Information" subtitle="Required fields">
			<div class="space-y-4">
				<div>
					<label for="name" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Name <span class="text-error-500">*</span>
					</label>
					<input
						id="name"
						name="name"
						type="text"
						bind:value={form.name}
						on:change={handleChange}
						required
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
						placeholder="Enter entity name"
					/>
				</div>

				<div>
					<label for="entity_type" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Type <span class="text-error-500">*</span>
						<span class="ml-2 inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100 align-middle">New</span>
					</label>
					<select
						id="entity_type"
						name="entity_type"
						bind:value={form.entity_type}
						on:change={handleChange}
						required
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
					>
						{#each entityTypes as type}
							<option value={type.value}>{type.label}{['division','function','section','unit'].includes(type.value) ? ' (New)' : ''}</option>
						{/each}
					</select>
				</div>

				<div>
					<label for="description" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Description
					</label>
					<textarea
						id="description"
						name="description"
						bind:value={form.description}
						on:change={handleChange}
						rows="3"
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
						placeholder="Enter entity description"
					></textarea>
				</div>

				<div>
					<label for="objectives" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Objectives
					</label>
					<textarea
						id="objectives"
						name="objectives"
						bind:value={form.objectives}
						on:change={handleChange}
						rows="3"
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
						placeholder="Enter the objectives or responsibilities of this entity"
					></textarea>
				</div>

				<div>
					<label for="parent" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Parent Entity
					</label>
					<select
						id="parent"
						name="parent"
						bind:value={form.parent}
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
					>
						<option value={null}>None (top-level entity)</option>
						{#each entities as entity}
							<option value={entity.id}>{entity.name} ({formatEntityType(entity.entity_type)})</option>
						{/each}
					</select>
				</div>
			</div>
		</FormSection>

		<!-- Team Assignment Section -->
		<FormSection title="Team Assignment" subtitle="Owner and team members" collapsible={true} defaultOpen={true}>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div>
					<label for="owner" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
						<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						Owner/Lead
					</label>
					<select
						id="owner"
						name="owner"
						bind:value={form.owner}
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
					>
						<option value={null}>Select owner (optional)</option>
						{#each users as user}
							<option value={user.id}>{user.first_name} {user.last_name} ({user.username})</option>
						{/each}
					</select>
				</div>

				<div>
					<label for="team_member" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
						<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
						</svg>
						Team Member
					</label>
					<select
						id="team_member"
						name="team_member"
						bind:value={form.team_member}
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
					>
						<option value={null}>Select team member (optional)</option>
						{#each users as user}
							<option value={user.id}>{user.first_name} {user.last_name} ({user.username})</option>
						{/each}
					</select>
				</div>
			</div>
		</FormSection>

		<!-- Legacy Contact Information (for backward compatibility) -->
		<FormSection title="Legacy Contact Information" subtitle="Deprecated - use Team Assignment above" collapsible={true} defaultOpen={false}>
			<div class="space-y-4">
				<div class="bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800 rounded-lg p-3 mb-4">
					<div class="flex items-start gap-2">
						<svg class="w-5 h-5 text-warning-600 dark:text-warning-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-1.856-1.333-2.626 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
						<p class="text-sm text-warning-800 dark:text-warning-200">
							⚠️ This section is deprecated. Please use "Team Assignment" above to assign Owner and Team Member.
						</p>
					</div>
				</div>

				<div>
					<label for="contact_type" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Contact Type
					</label>
					<select
						id="contact_type"
						name="contact_type"
						bind:value={form.contact_type}
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
					>
						<option value="owner">Owner</option>
						<option value="key_contact">Key Contact</option>
					</select>
				</div>

				<div>
					<label for="key_contact" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Key Contact
					</label>
					<select
						id="key_contact"
						name="key_contact"
						bind:value={form.key_contact}
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
					>
						<option value={null}>Select key contact (optional)</option>
						{#each users as user}
							<option value={user.id}>{user.username} ({user.email})</option>
						{/each}
					</select>
				</div>
			</div>
		</FormSection>


		<!-- Risk Assessment Section -->
		<FormSection title="Risk Assessment" subtitle="Risk scoring" collapsible={true} defaultOpen={false}>
			<div class="space-y-4">
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label for="risk_score" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Overall Risk Score
						</label>
						<input
							id="risk_score"
							name="risk_score"
							type="number"
							step="0.1"
							min="0"
							max="10"
							bind:value={form.risk_score}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							placeholder="0-10"
						/>
					</div>

					<div>
						<label for="inherent_risk_score" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Inherent Risk Score
						</label>
						<input
							id="inherent_risk_score"
							name="inherent_risk_score"
							type="number"
							step="0.1"
							min="0"
							max="10"
							bind:value={form.inherent_risk_score}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							placeholder="0-10"
						/>
					</div>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label for="residual_risk_score" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Residual Risk Score
						</label>
						<input
							id="residual_risk_score"
							name="residual_risk_score"
							type="number"
							step="0.1"
							min="0"
							max="10"
							bind:value={form.residual_risk_score}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							placeholder="0-10"
						/>
					</div>

					<div>
						<label for="control_maturity" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Control Maturity Level
						</label>
						<div class="flex items-center gap-3">
							<input
								id="control_maturity"
								name="control_maturity"
								type="range"
								min="0"
								max="5"
								step="1"
								bind:value={form.control_maturity}
								on:change={handleChange}
								class="flex-1 h-2 bg-surface-200 dark:bg-surface-700 rounded-lg appearance-none cursor-pointer"
							/>
							<span class="text-sm font-semibold text-surface-900 dark:text-surface-50 min-w-[2rem] text-center px-2 py-1 bg-surface-100 dark:bg-surface-800 rounded">
								{form.control_maturity || 0}
							</span>
						</div>
						<div class="grid grid-cols-6 text-[10px] text-surface-500 dark:text-surface-400 mt-2">
							<span>Initial</span>
							<span>Managed</span>
							<span>Defined</span>
							<span>Quantified</span>
							<span>Optimizing</span>
							<span>Advanced</span>
						</div>
					</div>
				</div>

				<div>
					<label for="regulatory_relevance" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Regulatory Relevance
					</label>
					<textarea
						id="regulatory_relevance"
						name="regulatory_relevance"
						bind:value={form.regulatory_relevance}
						on:change={handleRegulatoryRelevanceChange}
						rows="2"
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
						placeholder="Enter regulatory relevance (JSON or text)"
					></textarea>
				</div>
			</div>
		</FormSection>

		<!-- Audit Planning Section -->
		<FormSection title="Audit Planning" subtitle="Scheduling & priorities" collapsible={true} defaultOpen={false}>
			<div class="space-y-4">
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div>
						<label for="criticality" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Criticality
						</label>
						<select
							id="criticality"
							name="criticality"
							bind:value={form.criticality}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
						>
							{#each criticalityChoices as choice}
								<option value={choice.value}>{choice.label}</option>
							{/each}
						</select>
					</div>

					<div>
						<label for="priority" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Priority
						</label>
						<select
							id="priority"
							name="priority"
							bind:value={form.priority}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
						>
							{#each priorityChoices as choice}
								<option value={choice.value}>{choice.label}</option>
							{/each}
						</select>
					</div>

					<div>
						<label for="audit_frequency" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Audit Frequency
						</label>
						<select
							id="audit_frequency"
							name="audit_frequency"
							bind:value={form.audit_frequency}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
						>
							{#each auditFrequencyChoices as choice}
								<option value={choice.value}>{choice.label}</option>
							{/each}
						</select>
					</div>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label for="last_audited" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Last Audited
						</label>
						<input
							id="last_audited"
							name="last_audited"
							type="date"
							bind:value={form.last_audited}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
						/>
					</div>

					<div>
						<label for="next_audit_date" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Next Audit Date
						</label>
						<input
							id="next_audit_date"
							name="next_audit_date"
							type="date"
							bind:value={form.next_audit_date}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
						/>
					</div>
				</div>
			</div>
		</FormSection>

		<!-- Geographical Location Section -->
		<FormSection title="Geographical Location" badge="New" collapsible={true} defaultOpen={false}>
			<div class="space-y-4">
				<!-- Legacy location field for backward compatibility -->
				<div class="bg-surface-50 dark:bg-surface-800/50 border border-surface-200 dark:border-surface-700 rounded-lg p-3">
					<label for="location" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Legacy Location <span class="text-xs text-surface-500">(Optional)</span>
					</label>
					<input
						id="location"
						name="location"
						type="text"
						bind:value={form.location}
						on:change={handleChange}
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
						placeholder="Enter jurisdiction/region (e.g., US, EU, APAC)"
					/>
					<p class="text-xs text-surface-500 dark:text-surface-400 mt-1">⚠️ For backward compatibility. Use structured fields below for new entries.</p>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div>
						<label for="country" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Country
						</label>
						<input
							id="country"
							name="country"
							type="text"
							bind:value={form.country}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							placeholder="e.g., United States"
						/>
					</div>

					<div>
						<label for="region" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Region/State/Province
						</label>
						<input
							id="region"
							name="region"
							type="text"
							bind:value={form.region}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							placeholder="e.g., California"
						/>
					</div>

					<div>
						<label for="city" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							City
						</label>
						<input
							id="city"
							name="city"
							type="text"
							bind:value={form.city}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							placeholder="e.g., San Francisco"
						/>
					</div>
				</div>

				<div>
					<label for="address" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Address
					</label>
					<textarea
						id="address"
						name="address"
						bind:value={form.address}
						on:change={handleChange}
						rows="2"
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
						placeholder="Enter full physical address"
					></textarea>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label for="postal_code" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Postal/ZIP Code
						</label>
						<input
							id="postal_code"
							name="postal_code"
							type="text"
							bind:value={form.postal_code}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							placeholder="e.g., 94105"
						/>
					</div>

					<div>
						<label for="timezone" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Timezone
						</label>
						<select
							id="timezone"
							name="timezone"
							bind:value={form.timezone}
							on:change={handleChange}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
						>
							{#each commonTimezones as tz}
								<option value={tz.value}>{tz.label}</option>
							{/each}
						</select>
					</div>
				</div>

				<!-- Coordinates Section -->
				<div>
					<span class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
						Coordinates <span class="text-xs text-surface-500">(Optional)</span>
					</span>
					<div class="grid grid-cols-1 md:grid-cols-3 gap-3">
						<div>
							<label for="latitude" class="block text-xs text-surface-600 dark:text-surface-400 mb-1">
								Latitude
							</label>
							<input
								id="latitude"
								type="number"
								step="any"
								min="-90"
								max="90"
								value={form.coordinates?.latitude || ''}
								on:input={(e) => {
									const target = e.currentTarget as HTMLInputElement;
									handleCoordinateChange(target.value, form.coordinates?.longitude?.toString() || '');
								}}
								class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
								placeholder="37.7749"
							/>
						</div>

						<div>
							<label for="longitude" class="block text-xs text-surface-600 dark:text-surface-400 mb-1">
								Longitude
							</label>
							<input
								id="longitude"
								type="number"
								step="any"
								min="-180"
								max="180"
								value={form.coordinates?.longitude || ''}
								on:input={(e) => {
									const target = e.currentTarget as HTMLInputElement;
									handleCoordinateChange(form.coordinates?.latitude?.toString() || '', target.value);
								}}
								class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
								placeholder="-122.4194"
							/>
						</div>

						<div class="flex items-end">
							<button
								type="button"
								on:click={clearCoordinates}
								class="w-full px-3 py-2 text-sm text-surface-600 dark:text-surface-300 border border-surface-300 dark:border-surface-600 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors"
							>
								Clear
							</button>
						</div>
					</div>
					<p class="text-xs text-surface-500 dark:text-surface-400 mt-1.5">📍 Enter latitude (-90 to 90) and longitude (-180 to 180) for precise location mapping.</p>
				</div>
			</div>
		</FormSection>

		<!-- Additional Information Section -->
		<FormSection title="Additional Information" subtitle="Notes & attachments" collapsible={true} defaultOpen={false}>
			<div class="space-y-4">
				<div>
					<label for="org-structure" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Organizational Structure <span class="text-xs text-surface-500">(Optional)</span>
					</label>
					<div class="relative">
						<input
							id="org-structure"
							type="file"
							accept=".pdf,.png,.jpg,.jpeg,.svg"
							on:change={(e) => {
								const input = e.currentTarget as HTMLInputElement;
								orgStructureFile = (input.files && input.files[0]) || null;
							}}
							class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 dark:file:bg-primary-900/20 file:text-primary-700 dark:file:text-primary-300 hover:file:bg-primary-100 dark:hover:file:bg-primary-900/30"
						/>
					</div>
					<p class="text-xs text-surface-500 dark:text-surface-400 mt-1.5">📎 PDF or image files are supported (max 10MB).</p>
				</div>

				<div>
					<label for="notes" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Notes
					</label>
					<textarea
						id="notes"
						name="notes"
						bind:value={form.notes}
						on:change={handleChange}
						rows="3"
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
						placeholder="Enter additional notes and observations"
					></textarea>
				</div>

				<div class="flex items-center gap-3 p-3 bg-surface-50 dark:bg-surface-800/50 rounded-lg">
					<input
						id="is_active"
						name="is_active"
						type="checkbox"
						bind:checked={form.is_active}
						on:change={handleChange}
						class="h-4 w-4 text-primary-600 focus:ring-2 focus:ring-primary-500 border-surface-300 dark:border-surface-600 rounded"
					/>
					<label for="is_active" class="text-sm font-medium text-surface-900 dark:text-surface-50 cursor-pointer select-none">
						Active Entity
					</label>
				</div>
			</div>
		</FormSection>

		<!-- Form Actions -->
		<div class="flex justify-end gap-3 pt-4 sticky bottom-0 bg-white dark:bg-surface-900 border-t border-surface-200 dark:border-surface-700 -mx-6 px-6 py-4">
			<button
				type="button"
				on:click={() => onSaved()}
				class="px-5 py-2.5 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm text-sm font-medium text-surface-700 dark:text-surface-300 bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
			>
				Cancel
			</button>
			<button
				type="submit"
				disabled={saving}
				class="px-5 py-2.5 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
			>
				{#if saving}
					<svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					Creating...
				{:else}
					<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
					</svg>
					Create Entity
				{/if}
			</button>
		</div>
	</form>
</div>

<style>
	.enhanced-modal-body {
		max-height: calc(100vh - 200px);
		overflow-y: auto;
		padding-right: 2px;
	}

	/* Custom scrollbar */
	.enhanced-modal-body::-webkit-scrollbar {
		width: 8px;
	}

	.enhanced-modal-body::-webkit-scrollbar-track {
		background: transparent;
	}

	.enhanced-modal-body::-webkit-scrollbar-thumb {
		background: rgba(0, 0, 0, 0.2);
		border-radius: 4px;
	}

	.enhanced-modal-body::-webkit-scrollbar-thumb:hover {
		background: rgba(0, 0, 0, 0.3);
	}
</style>
