<script>
	import { onMount } from 'svelte';
	import { 
		createEngagement, 
		updateEngagement, 
		getEngagement,
		ENGAGEMENT_STATUSES,
		ENGAGEMENT_PRIORITIES,
		AUDIT_TYPES
	} from './api.js';
	import { getUsers } from '../universe/users-api.js';
	import FormSection from '../universe/FormSection.svelte';

	export let engagementId = null;
	export let onSaved = () => {};
	export let onCancel = () => {};

	let form = {
		title: '',
		description: '',
		audit_plan: null,
		entity: null,
		status: 'draft',
		priority: 'medium',
		audit_type: 'internal',
		assigned_auditor: null,
		engagement_lead: null,
		planned_start_date: '',
		planned_end_date: '',
		actual_start_date: '',
		actual_end_date: '',
		scope: '',
		objectives: '',
		methodology: '',
		estimated_hours: null,
		actual_hours: null,
		budget_allocated: null,
		actual_cost: null,
		tags: [],
		is_active: true
	};
	
	let saving = false;
	let loading = false;
	let error = null;
	let auditPlans = [];
	let entities = [];
	let users = [];
	let formLoaded = false;

	onMount(async () => {
		await loadReferenceData();
		if (engagementId) {
			await loadEngagement();
		}
	});

	async function loadEngagement() {
		if (formLoaded) return; // Prevent multiple loads
		
		loading = true;
		try {
			const engagement = await getEngagement(engagementId);
			form = {
				title: engagement.title || '',
				description: engagement.description || '',
				audit_plan: engagement.audit_plan || null,
				entity: engagement.entity || null,
				status: engagement.status || 'draft',
				priority: engagement.priority || 'medium',
				audit_type: engagement.audit_type || 'internal',
				assigned_auditor: engagement.assigned_auditor || null,
				engagement_lead: engagement.engagement_lead || null,
				planned_start_date: engagement.planned_start_date || '',
				planned_end_date: engagement.planned_end_date || '',
				actual_start_date: engagement.actual_start_date || '',
				actual_end_date: engagement.actual_end_date || '',
				scope: engagement.scope || '',
				objectives: engagement.objectives || '',
				methodology: engagement.methodology || '',
				estimated_hours: engagement.estimated_hours || null,
				actual_hours: engagement.actual_hours || null,
				budget_allocated: engagement.budget_allocated || null,
				actual_cost: engagement.actual_cost || null,
				tags: engagement.tags || [],
				is_active: engagement.is_active !== false
			};
			formLoaded = true;
		} catch (err) {
			console.error('Error loading engagement:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	}

	async function loadReferenceData() {
		try {
			// Load audit plans from the real API
			const plansResponse = await fetch('/fe-api/audits/plans/');
			if (plansResponse.ok) {
				const plansData = await plansResponse.json();
				auditPlans = plansData.results || plansData;
			} else {
				console.error('Failed to load audit plans:', plansResponse.status);
				// Fallback to empty array if API fails
				auditPlans = [];
			}

			// Load entities from Audit Universe
			const entitiesResponse = await fetch('/fe-api/audits/entities/');
			if (entitiesResponse.ok) {
				const entitiesData = await entitiesResponse.json();
				entities = entitiesData.results || entitiesData;
			} else {
				console.error('Failed to load entities:', entitiesResponse.status);
				// Fallback to empty array if API fails
				entities = [];
			}

		// Load users from API
		try {
			const usersData = await getUsers();
			users = usersData.results || usersData || [];
		} catch (err) {
			console.error('Error loading users:', err);
			users = [];
		}
		} catch (err) {
			console.error('Error loading reference data:', err);
			// Set empty arrays as fallback
			auditPlans = [];
			entities = [];
			users = [];
		}
	}

	function handleChange(event) {
		const { name, value, type, checked } = event.target;
		
		// List of fields that are integer IDs (not UUID strings)
		const integerIdFields = ['audit_plan', 'entity'];
		// User IDs are UUIDs (strings), not integers
		const stringIdFields = ['assigned_auditor', 'engagement_lead'];
		
		let processedValue;
		if (type === 'checkbox') {
			processedValue = checked;
		} else if (type === 'number') {
			processedValue = value ? Number(value) : null;
		} else if (integerIdFields.includes(name)) {
			// Convert integer ID fields to integers, or null if empty
			processedValue = value && value !== '' ? parseInt(value) : null;
		} else if (stringIdFields.includes(name)) {
			// Keep string IDs (UUIDs) as strings, or null if empty
			processedValue = value && value !== '' ? value : null;
		} else {
			processedValue = value;
		}
		
		// Auto-select entity when audit plan changes
		if (name === 'audit_plan') {
			if (processedValue) {
				const selectedPlan = auditPlans.find(plan => plan.id === processedValue);
				if (selectedPlan && selectedPlan.entity) {
					form = {
						...form,
						[name]: processedValue,
						entity: selectedPlan.entity
					};
					return;
				}
			} else {
				// If audit plan is cleared, also clear entity
				form = {
					...form,
					[name]: null,
					entity: null
				};
				return;
			}
		}
		
		form = {
			...form,
			[name]: processedValue
		};
	}

	function handleArrayChange(name, value) {
		form = {
			...form,
			[name]: value.split(',').map(item => item.trim()).filter(item => item)
		};
	}

	async function handleSubmit(event) {
		event.preventDefault();
		saving = true;
		error = null;
		
		try {
			// Clean up form data
			const formData = { ...form };
			
			// Remove empty string values and convert them to null for optional fields
			// But keep numeric zeros and boolean false values
			Object.keys(formData).forEach(key => {
				if (formData[key] === '') {
					// For foreign key fields, delete empty strings (whether integer IDs or UUID strings)
					if (['audit_plan', 'entity', 'assigned_auditor', 'engagement_lead'].includes(key)) {
						delete formData[key];
					}
				}
				// Remove null values for POST requests (creating new engagement)
				// But keep them for PUT requests (updating) to allow clearing fields
				if (formData[key] === null && !engagementId) {
					delete formData[key];
				}
			});
			
			// Note: User IDs (assigned_auditor, engagement_lead) are UUIDs (strings), not integers
			// They should be sent as-is without conversion
			
			if (engagementId) {
				await updateEngagement(engagementId, formData);
			} else {
				await createEngagement(formData);
			}
			
			onSaved();
		} catch (err) {
			console.error('Error saving engagement:', err);
			error = err.message || 'Failed to save engagement';
		} finally {
			saving = false;
		}
	}

	function formatDate(dateString) {
		if (!dateString) return '';
		return new Date(dateString).toISOString().split('T')[0];
	}
</script>

<div class="mx-auto p-6">
	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-center gap-3 mb-2">
			<div class="p-3 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl shadow-lg">
				<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
				</svg>
			</div>
			<div>
				<h1 class="text-3xl font-bold text-surface-900 dark:text-surface-50">
					{engagementId ? 'Edit Engagement' : 'Create Engagement'}
				</h1>
				<p class="text-surface-600 dark:text-surface-400 mt-1">
					{engagementId ? 'Update the engagement details' : 'Create a new audit engagement within a planned audit'}
				</p>
			</div>
		</div>
	</div>

	<!-- Error State -->
	{#if error}
		<div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-4 mb-6 shadow-sm flex items-start gap-3">
			<svg class="h-5 w-5 text-error-600 dark:text-error-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<div class="text-error-800 dark:text-error-200">{error}</div>
		</div>
	{/if}

	<!-- Loading State -->
	{#if loading}
		<div class="flex justify-center items-center py-16">
			<div class="flex flex-col items-center gap-4">
				<svg class="animate-spin h-12 w-12 text-primary-600" fill="none" viewBox="0 0 24 24">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
				</svg>
				<span class="text-surface-600 dark:text-surface-400 font-medium">Loading engagement...</span>
			</div>
		</div>
	{:else}

		<!-- Form -->
		<form on:submit={handleSubmit} class="space-y-6">
			<!-- Basic Information -->
			<FormSection title="📋 Basic Information" subtitle="Essential details about the engagement" collapsible={false}>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div class="md:col-span-2">
						<label for="title" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
							Title <span class="text-error-500">*</span>
						</label>
						<input
							id="title"
							name="title"
							type="text"
							value={form.title}
							on:change={handleChange}
							required
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
							placeholder="Enter engagement title"
						/>
					</div>

					<div class="md:col-span-2">
						<label for="description" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
							Description
						</label>
						<textarea
							id="description"
							name="description"
							value={form.description}
							on:change={handleChange}
							rows="4"
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
							placeholder="Enter engagement description"
						></textarea>
					</div>

					<div>
					<label for="audit_plan" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
						Audit Plan <span class="text-error-500">*</span>
					</label>
					<select
						id="audit_plan"
						name="audit_plan"
						on:change={handleChange}
						required
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
					>
						<option value="" selected={!form.audit_plan}>Select audit plan</option>
						{#each auditPlans as plan}
							<option value={plan.id} selected={form.audit_plan === plan.id}>
								{plan.title}
								{#if plan.entity_name}
									- {plan.entity_name}
								{/if}
							</option>
						{/each}
					</select>
					</div>

					<div>
					<label for="entity" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
						Entity <span class="text-error-500">*</span>
						{#if form.audit_plan}
							<span class="text-sm text-primary-600 dark:text-primary-400 ml-2 font-normal">(Auto-selected)</span>
						{/if}
					</label>
					<select
						id="entity"
						name="entity"
						on:change={handleChange}
						required
						disabled={form.audit_plan}
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors {form.audit_plan ? 'opacity-60 cursor-not-allowed' : ''}"
					>
						<option value="" selected={!form.entity}>Select entity</option>
						{#each entities as entity}
							<option value={entity.id} selected={form.entity === entity.id}>{entity.name}</option>
						{/each}
					</select>
						{#if form.audit_plan}
							<p class="mt-2 text-xs text-surface-500 dark:text-surface-400">💡 Entity is automatically selected based on the chosen audit plan.</p>
						{/if}
					</div>

					<div>
					<label for="status" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
						Status
					</label>
					<select
						id="status"
						name="status"
						on:change={handleChange}
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
					>
						{#each ENGAGEMENT_STATUSES as status}
							<option value={status.value} selected={form.status === status.value}>{status.label}</option>
						{/each}
					</select>
					</div>

					<div>
					<label for="priority" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
						Priority
					</label>
					<select
						id="priority"
						name="priority"
						on:change={handleChange}
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
					>
						{#each ENGAGEMENT_PRIORITIES as priority}
							<option value={priority.value} selected={form.priority === priority.value}>{priority.label}</option>
						{/each}
					</select>
					</div>

					<div>
					<label for="audit_type" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
						Audit Type
					</label>
					<select
						id="audit_type"
						name="audit_type"
						on:change={handleChange}
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
					>
						{#each AUDIT_TYPES as auditType}
							<option value={auditType.value} selected={form.audit_type === auditType.value}>{auditType.label}</option>
						{/each}
					</select>
					</div>
				</div>
			</FormSection>

			<!-- Assignment -->
			<FormSection title="👥 Assignment" subtitle="Team members and responsibilities" collapsible={false}>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<label for="assigned_auditor" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
							Assigned Auditor
						</label>
						<select
							id="assigned_auditor"
							name="assigned_auditor"
							on:change={handleChange}
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
						>
							<option value="" selected={!form.assigned_auditor}>Select auditor</option>
							{#each users as user}
								<option value={user.id} selected={form.assigned_auditor === user.id}>{user.first_name} {user.last_name} ({user.username})</option>
							{/each}
						</select>
					</div>

					<div>
						<label for="engagement_lead" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Engagement Lead
						</label>
						<select
							id="engagement_lead"
							name="engagement_lead"
							on:change={handleChange}
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
						>
							<option value="" selected={!form.engagement_lead}>Select lead</option>
							{#each users as user}
								<option value={user.id} selected={form.engagement_lead === user.id}>{user.first_name} {user.last_name} ({user.username})</option>
							{/each}
						</select>
					</div>
				</div>
			</FormSection>

			<!-- Schedule -->
			<FormSection title="📅 Schedule" subtitle="Plan the engagement timeline" collapsible={false}>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<label for="planned_start_date" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
							</svg>
							Planned Start Date <span class="text-error-500">*</span>
						</label>
						<input
							id="planned_start_date"
							name="planned_start_date"
							type="date"
							value={form.planned_start_date}
							on:change={handleChange}
							required
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
						/>
					</div>

					<div>
						<label for="planned_end_date" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Planned End Date <span class="text-error-500">*</span>
						</label>
						<input
							id="planned_end_date"
							name="planned_end_date"
							type="date"
							value={form.planned_end_date}
							on:change={handleChange}
							required
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
						/>
					</div>

					<div>
						<label for="actual_start_date" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
							</svg>
							Actual Start Date
						</label>
						<input
							id="actual_start_date"
							name="actual_start_date"
							type="date"
							value={form.actual_start_date}
							on:change={handleChange}
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
						/>
						{#if form.actual_start_date && form.planned_start_date && form.actual_start_date !== form.planned_start_date}
							<p class="mt-2 text-xs text-warning-600 dark:text-warning-400">
								⚠️ Actual start date differs from planned date
							</p>
						{/if}
					</div>

					<div>
						<label for="actual_end_date" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Actual End Date
						</label>
						<input
							id="actual_end_date"
							name="actual_end_date"
							type="date"
							value={form.actual_end_date}
							on:change={handleChange}
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
						/>
						{#if form.actual_end_date && form.planned_end_date && form.actual_end_date !== form.planned_end_date}
							<p class="mt-2 text-xs text-warning-600 dark:text-warning-400">
								⚠️ Actual end date differs from planned date
							</p>
						{/if}
					</div>
				</div>
			</FormSection>

			<!-- Scope & Objectives -->
			<FormSection title="🎯 Scope & Objectives" subtitle="Define engagement scope and methodology" collapsible={false}>
				<div class="space-y-6">
					<div>
						<label for="scope" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
							Scope
						</label>
						<textarea
							id="scope"
							name="scope"
							value={form.scope}
							on:change={handleChange}
							rows="5"
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
							placeholder="• Define what is included in this engagement&#10;• Specify areas, processes, or systems to review&#10;• Note any exclusions or limitations"
						></textarea>
					</div>

					<div>
						<label for="objectives" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
							</svg>
							Objectives
						</label>
						<textarea
							id="objectives"
							name="objectives"
							value={form.objectives}
							on:change={handleChange}
							rows="5"
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
							placeholder="• List the primary objectives of this engagement&#10;• What are the key questions to answer?&#10;• What outcomes are expected?"
						></textarea>
					</div>

					<div>
						<label for="methodology" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
							Methodology
						</label>
						<textarea
							id="methodology"
							name="methodology"
							value={form.methodology}
							on:change={handleChange}
							rows="5"
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
							placeholder="• Describe the audit approach and methods&#10;• List techniques and tools to be used&#10;• Outline the testing procedures"
						></textarea>
					</div>
				</div>
			</FormSection>

			<!-- Resources -->
			<FormSection title="💼 Resources" subtitle="Budget and time tracking" collapsible={false}>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<label for="estimated_hours" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Estimated Hours
						</label>
						<input
							id="estimated_hours"
							name="estimated_hours"
							type="number"
							min="0"
							value={form.estimated_hours}
							on:change={handleChange}
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
							placeholder="Enter estimated hours"
						/>
					</div>

					<div>
						<label for="budget_allocated" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Budget Allocated
						</label>
						<input
							id="budget_allocated"
							name="budget_allocated"
							type="number"
							step="0.01"
							min="0"
							value={form.budget_allocated}
							on:change={handleChange}
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
							placeholder="Enter budget amount"
						/>
					</div>

					<div>
						<label for="actual_hours" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Actual Hours
						</label>
						<input
							id="actual_hours"
							name="actual_hours"
							type="number"
							min="0"
							value={form.actual_hours}
							on:change={handleChange}
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
							placeholder="Enter actual hours worked"
						/>
					</div>

					<div>
						<label for="actual_cost" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
							</svg>
							Actual Cost
						</label>
						<input
							id="actual_cost"
							name="actual_cost"
							type="number"
							step="0.01"
							min="0"
							value={form.actual_cost}
							on:change={handleChange}
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
							placeholder="Enter actual cost incurred"
						/>
					</div>
				</div>
			</FormSection>

			<!-- Additional Information -->
			<FormSection title="📝 Additional Information" subtitle="Tags and settings" collapsible={false}>
				<div class="space-y-6">
					<div>
						<label for="tags" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
							</svg>
							Tags (comma-separated)
						</label>
						<input
							id="tags"
							name="tags"
							type="text"
							value={form.tags.join(', ')}
							on:change={(e) => handleArrayChange('tags', e.target?.value || '')}
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
							placeholder="Enter tags separated by commas (e.g., compliance, security, critical)"
						/>
					</div>

					<div class="flex items-center gap-3 p-4 bg-surface-50 dark:bg-surface-800/50 rounded-xl border-2 border-surface-200 dark:border-surface-700">
						<input
							id="is_active"
							name="is_active"
							type="checkbox"
							checked={form.is_active}
							on:change={handleChange}
							class="h-4 w-4 text-primary-600 focus:ring-2 focus:ring-primary-500 border-surface-300 dark:border-surface-600 rounded"
						/>
						<label for="is_active" class="text-sm font-semibold text-surface-900 dark:text-surface-50 cursor-pointer select-none">
							Active Engagement
						</label>
					</div>
				</div>
			</FormSection>

			<!-- Actions -->
			<div class="sticky bottom-0 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-900 dark:to-surface-800 border-t-2 border-surface-200 dark:border-surface-700 p-6 rounded-xl shadow-xl mt-8">
				<div class="flex justify-end gap-3">
					<button
						type="button"
						on:click={onCancel}
						class="px-6 py-3 border-2 border-surface-300 dark:border-surface-600 rounded-xl shadow-sm text-sm font-semibold text-surface-700 dark:text-surface-200 bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all flex items-center gap-2"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
						Cancel
					</button>
					<button
						type="submit"
						disabled={saving}
						class="px-6 py-3 border-2 border-transparent rounded-xl shadow-lg text-sm font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 min-w-[180px] justify-center"
					>
						{#if saving}
							<svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							{engagementId ? 'Updating...' : 'Creating...'}
						{:else}
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
							</svg>
							{engagementId ? 'Update Engagement' : 'Create Engagement'}
						{/if}
					</button>
				</div>
			</div>
		</form>
	{/if}
</div>

