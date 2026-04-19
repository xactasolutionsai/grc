<script lang="ts">
	import { onMount } from 'svelte';
	import { createPlan, updatePlan, getPlan } from './api.js';
	import { listEntities } from '../universe/api.js';
	import { getUsers } from '../universe/users-api.js';
	import FormSection from '../universe/FormSection.svelte';

	interface AuditEntity {
		id: number;
		name: string;
		entity_type: string;
	}

	interface User {
		id: number;
		username: string;
		email: string;
	}

	interface AuditTeamMember {
		user_id: number;
		role: string;
		username: string;
		email: string;
	}

	interface AuditPlan {
		id?: number;
		entity: number | null;
		auditable_entities: number[];
		title: string;
		description: string;
		planned_start: string;
		planned_end: string;
		actual_start: string;
		actual_end: string;
		lead_auditor: number | null;
		audit_team: AuditTeamMember[];
		status: string;
		objectives: string;
		scope: string;
		resources: any;
	}

	// Props
	let { planId, entityId, onSaved }: { planId?: number; entityId?: number | null; onSaved: () => void } = $props();

	// State
	let form = $state<AuditPlan>({
		entity: null,
		auditable_entities: [],
		title: '',
		description: '',
		planned_start: '',
		planned_end: '',
		actual_start: '',
		actual_end: '',
		lead_auditor: null,
		audit_team: [],
		status: 'planned',
		objectives: '',
		scope: '',
		resources: null
	});

	let entities = $state<AuditEntity[]>([]);
	let users = $state<User[]>([]);
	let loading = $state(false);
	let saving = $state(false);
	let error = $state('');

	// Status choices with icons
	const statusChoices = [
		{ value: 'draft', label: '📝 Draft', icon: '📝' },
		{ value: 'pending_approval', label: '⏳ Pending Approval', icon: '⏳' },
		{ value: 'approved', label: '✅ Approved', icon: '✅' },
		{ value: 'in_review', label: '🔍 In Review', icon: '🔍' },
		{ value: 'in_progress', label: '🚀 In Progress', icon: '🚀' },
		{ value: 'completed', label: '🎉 Completed', icon: '🎉' },
		{ value: 'cancelled', label: '❌ Cancelled', icon: '❌' }
	];

	// Audit team roles
	const auditTeamRoles = [
		{ value: 'lead_auditor', label: 'Lead Auditor' },
		{ value: 'senior_auditor', label: 'Senior Auditor' },
		{ value: 'junior_auditor', label: 'Junior Auditor' },
		{ value: 'auditor', label: 'Auditor' }
	];

	onMount(async () => {
		await Promise.all([loadEntities(), loadUsers()]);

		if (planId) {
			await loadPlan();
		} else if (entityId) {
			// Pre-select the entity if provided
			form.entity = entityId;
		}
	});

	async function loadEntities() {
		try {
			const data = await listEntities();
			entities = data.results || [];
		} catch (err: any) {
			console.error('Error loading entities:', err);
			error = 'Failed to load entities';
		}
	}

	async function loadUsers() {
		try {
			const data = await getUsers();
			users = data.results || data || [];
		} catch (err: any) {
			console.error('Error loading users:', err);
			users = [];
			// Don't set error since this is not critical
		}
	}

	async function loadPlan() {
		if (!planId) return;

		try {
			loading = true;
			const plan = await getPlan(planId);

			form = {
				id: plan.id,
				entity: plan.entity,
				auditable_entities: plan.auditable_entities || [],
				title: plan.title,
				description: plan.description || '',
				planned_start: plan.planned_start,
				planned_end: plan.planned_end,
				actual_start: plan.actual_start || '',
				actual_end: plan.actual_end || '',
				lead_auditor: plan.lead_auditor,
				audit_team: plan.audit_team || [],
				status: plan.status,
				objectives: plan.objectives || '',
				scope: plan.scope || '',
				resources: plan.resources
			};
		} catch (err: any) {
			console.error('Error loading plan:', err);
			error = 'Failed to load audit plan';
		} finally {
			loading = false;
		}
	}

	// Audit Team Management Functions
	function addTeamMember() {
		const newMember = {
			user_id: 0,
			role: 'auditor',
			username: '',
			email: ''
		};
		form.audit_team = [...form.audit_team, newMember];
	}

	function removeTeamMember(index: number) {
		form.audit_team = form.audit_team.filter((_, i) => i !== index);
	}

	function updateTeamMember(index: number, field: string, value: any) {
		const updatedTeam = [...form.audit_team];

		if (field === 'user_id') {
			const userId = parseInt(value);
			const user = users.find(u => u.id === userId);
			if (user) {
				updatedTeam[index] = {
					...updatedTeam[index],
					user_id: user.id,
					username: user.username,
					email: user.email
				};
			} else {
				// No valid user selected (or "Select user..." option chosen)
				updatedTeam[index] = {
					...updatedTeam[index],
					user_id: userId,
					username: '',
					email: ''
				};
			}
		} else {
			updatedTeam[index] = {
				...updatedTeam[index],
				[field]: value
			};
		}

		form.audit_team = updatedTeam;
	}

	// Auditable Entities Management Functions
	function toggleEntity(entityId: number) {
		if (form.auditable_entities.includes(entityId)) {
			form.auditable_entities = form.auditable_entities.filter(id => id !== entityId);
		} else {
			form.auditable_entities = [...form.auditable_entities, entityId];
		}
	}

	async function savePlan() {
		try {
			saving = true;
			error = '';

			// Validate required fields
			if (!form.title.trim()) {
				error = 'Title is required';
				return;
			}
			if (!form.entity) {
				error = 'Entity is required';
				return;
			}
			if (!form.planned_start) {
				error = 'Planned start date is required';
				return;
			}
			if (!form.planned_end) {
				error = 'Planned end date is required';
				return;
			}
			if (new Date(form.planned_end) < new Date(form.planned_start)) {
				error = 'Planned end date must be after planned start date';
				return;
			}

		// Validate audit team (must have at least one Lead Auditor if team is not empty)
		if (form.audit_team.length > 0) {
			const hasLeadAuditor = form.audit_team.some(member => member.role === 'lead_auditor');
			if (!hasLeadAuditor) {
				error = 'At least one Lead Auditor must be assigned to the audit team';
				return;
			}

			// Check that all team members have a user selected
			// Handle both string and number comparison (HTML select values are strings)
			const invalidMembers: any[] = [];
			form.audit_team.forEach((member, idx) => {
				const userId = typeof member.user_id === 'string' ? parseInt(member.user_id) : member.user_id;
				if (!userId || userId === 0 || isNaN(userId)) {
					invalidMembers.push({ index: idx, member });
				}
			});

			if (invalidMembers.length > 0) {
				error = 'All team members must have a user selected';
				return;
			}
		}

			// Validate actual dates
			if (form.actual_start && form.planned_start) {
				if (new Date(form.actual_start) < new Date(form.planned_start)) {
					error = 'Actual start date cannot be before planned start date';
					return;
				}
			}
			if (form.actual_end && form.actual_start) {
				if (new Date(form.actual_end) < new Date(form.actual_start)) {
					error = 'Actual end date must be after actual start date';
					return;
				}
			}

			// Prepare data for API
			const planData: any = {
				entity: form.entity,
				auditable_entities: form.auditable_entities,
				title: form.title.trim(),
				description: form.description.trim(),
				planned_start: form.planned_start,
				planned_end: form.planned_end,
				actual_start: form.actual_start || null,
				actual_end: form.actual_end || null,
				lead_auditor: form.lead_auditor,
				audit_team: form.audit_team.length > 0 ? form.audit_team : null,
				status: form.status,
				objectives: form.objectives.trim(),
				scope: form.scope.trim(),
				resources: form.resources
			};

			if (planId) {
				await updatePlan(planId, planData);
			} else {
				await createPlan(planData);
			}

			onSaved();
		} catch (err: any) {
			console.error('Error saving plan:', err);
			error = err.message || 'Failed to save audit plan';
		} finally {
			saving = false;
		}
	}

	function resetForm() {
		form = {
			entity: null,
			auditable_entities: [],
			title: '',
			description: '',
			planned_start: '',
			planned_end: '',
			actual_start: '',
			actual_end: '',
			lead_auditor: null,
			audit_team: [],
			status: 'draft',
			objectives: '',
			scope: '',
			resources: null
		};
		error = '';
	}
</script>

<div class="mx-auto p-6">
	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-center gap-3 mb-2">
			<div class="p-3 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl shadow-lg">
				<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
				</svg>
			</div>
			<div>
				<h1 class="text-3xl font-bold text-surface-900 dark:text-surface-50">
					{planId ? 'Edit Audit Plan' : 'Create Audit Plan'}
				</h1>
				<p class="text-surface-600 dark:text-surface-400 mt-1">
					{planId ? 'Update the audit plan details' : 'Plan a new audit engagement for an entity in your audit universe'}
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
				<span class="text-surface-600 dark:text-surface-400 font-medium">Loading audit plan...</span>
			</div>
		</div>
	{:else}
		<!-- Form -->
		<form onsubmit={(e) => { e.preventDefault(); savePlan(); }} class="space-y-6">
			<!-- Basic Information -->
			<FormSection title="📋 Basic Information" subtitle="Essential details about the audit plan" collapsible={false}>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<!-- Title -->
					<div class="md:col-span-2">
						<label for="title" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
							Title <span class="text-error-500">*</span>
						</label>
						<input
							id="title"
							type="text"
							bind:value={form.title}
							required
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
							placeholder="Enter audit plan title"
						/>
					</div>

				<!-- Entity -->
				<div>
					<label for="entity" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
						Entity <span class="text-error-500">*</span>
					</label>
					<select
						id="entity"
						onchange={(e) => {
							const value = (e.target as HTMLSelectElement).value;
							form.entity = value ? parseInt(value) : null;
						}}
						required
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
					>
						<option value="" selected={!form.entity}>Select an entity</option>
						{#each entities as entity}
							<option value={entity.id} selected={form.entity === entity.id}>
								{#if entity.entity_type === 'business_unit'}🏢
								{:else if entity.entity_type === 'division'}🔷
								{:else if entity.entity_type === 'function'}⚙️
								{:else if entity.entity_type === 'section'}📑
								{:else if entity.entity_type === 'unit'}📦
								{:else if entity.entity_type === 'process'}🔄
								{:else if entity.entity_type === 'system'}💻
								{:else if entity.entity_type === 'vendor'}🤝
								{:else if entity.entity_type === 'compliance_domain'}📋
								{:else if entity.entity_type === 'audit_domain'}🎯
								{:else}📄
								{/if}
								{entity.name} ({entity.entity_type.replace('_', ' ')})
							</option>
						{/each}
					</select>
				</div>

					<!-- Auditable Entities -->
					<div class="md:col-span-2">
						<label class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
							Additional Auditable Entities
							<span class="text-xs text-surface-500 dark:text-surface-400 ml-2 font-normal">(Optional - Select entities relevant to this audit)</span>
						</label>
						<div class="border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 rounded-xl p-4 max-h-48 overflow-y-auto">
							{#if entities.length === 0}
								<p class="text-sm text-surface-500 dark:text-surface-400">No entities available</p>
							{:else}
								<div class="space-y-2">
									{#each entities as entity}
										<label class="flex items-center gap-3 p-2 hover:bg-surface-50 dark:hover:bg-surface-800 rounded-lg cursor-pointer transition-colors">
											<input
												type="checkbox"
												checked={form.auditable_entities.includes(entity.id)}
												onchange={() => toggleEntity(entity.id)}
												class="h-4 w-4 text-primary-600 focus:ring-2 focus:ring-primary-500 border-surface-300 dark:border-surface-600 rounded"
											/>
											<span class="text-sm text-surface-900 dark:text-surface-50">
												{#if entity.entity_type === 'business_unit'}🏢
												{:else if entity.entity_type === 'division'}🔷
												{:else if entity.entity_type === 'function'}⚙️
												{:else if entity.entity_type === 'section'}📑
												{:else if entity.entity_type === 'unit'}📦
												{:else if entity.entity_type === 'process'}🔄
												{:else if entity.entity_type === 'system'}💻
												{:else if entity.entity_type === 'vendor'}🤝
												{:else if entity.entity_type === 'compliance_domain'}📋
												{:else if entity.entity_type === 'audit_domain'}🎯
												{:else}📄
												{/if}
												{entity.name}
												<span class="text-xs text-surface-500 dark:text-surface-400">({entity.entity_type.replace('_', ' ')})</span>
											</span>
										</label>
									{/each}
								</div>
							{/if}
						</div>
						{#if form.auditable_entities.length > 0}
							<p class="mt-2 text-xs text-surface-600 dark:text-surface-400">
								✓ {form.auditable_entities.length} entit{form.auditable_entities.length === 1 ? 'y' : 'ies'} selected
							</p>
						{/if}
					</div>

				<!-- Status -->
				<div>
					<label for="status" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
						Status
					</label>
					<select
						id="status"
						onchange={(e) => {
							const value = (e.target as HTMLSelectElement).value;
							form.status = value;
						}}
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
					>
						{#each statusChoices as choice}
							<option value={choice.value} selected={form.status === choice.value}>
								{choice.label}
							</option>
						{/each}
					</select>
				</div>

					<!-- Description -->
					<div class="md:col-span-2">
						<label for="description" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
							Description
						</label>
						<textarea
							id="description"
							bind:value={form.description}
							rows="4"
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
							placeholder="Enter audit plan description"
						></textarea>
					</div>
				</div>
			</FormSection>

			<!-- Timeline -->
			<FormSection title="📅 Timeline" subtitle="Plan the audit duration and track actual dates" collapsible={false}>
				<div class="space-y-6">
					<!-- Planned Dates -->
					<div>
						<h4 class="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-3">Planned Dates</h4>
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<!-- Planned Start -->
							<div>
								<label for="planned_start" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
									<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
									</svg>
									Planned Start Date <span class="text-error-500">*</span>
								</label>
								<input
									id="planned_start"
									type="date"
									bind:value={form.planned_start}
									required
									class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
								/>
							</div>

							<!-- Planned End -->
							<div>
								<label for="planned_end" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
									<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
									</svg>
									Planned End Date <span class="text-error-500">*</span>
								</label>
								<input
									id="planned_end"
									type="date"
									bind:value={form.planned_end}
									required
									class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
								/>
							</div>
						</div>
					</div>

					<!-- Actual Dates -->
					<div>
						<h4 class="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2">Actual Dates</h4>
						<p class="text-xs text-surface-500 dark:text-surface-400 mb-3">Fill in actual dates as the audit progresses</p>
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<!-- Actual Start -->
							<div>
								<label for="actual_start" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
									<svg class="w-4 h-4 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
									</svg>
									Actual Start Date
								</label>
								<input
									id="actual_start"
									type="date"
									bind:value={form.actual_start}
									class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 transition-colors"
								/>
							</div>

							<!-- Actual End -->
							<div>
								<label for="actual_end" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
									<svg class="w-4 h-4 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
									</svg>
									Actual End Date
								</label>
								<input
									id="actual_end"
									type="date"
									bind:value={form.actual_end}
									class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 transition-colors"
								/>
							</div>
						</div>
					</div>
				</div>
			</FormSection>

			<!-- Audit Team -->
			<FormSection title="👥 Audit Team" subtitle="Assign team members with their roles" collapsible={false}>
				<div class="space-y-4">
					<div class="flex items-center justify-between mb-4">
						<p class="text-sm text-surface-600 dark:text-surface-400">
							Build your audit team by assigning members with specific roles. At least one Lead Auditor is required.
						</p>
						<button
							type="button"
							onclick={addTeamMember}
							class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold rounded-lg transition-colors shadow-sm"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							Add Team Member
						</button>
					</div>

					{#if form.audit_team.length === 0}
						<div class="border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-xl p-8 text-center">
							<svg class="mx-auto h-12 w-12 text-surface-400 dark:text-surface-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
							</svg>
							<p class="text-surface-600 dark:text-surface-400 text-sm">No team members assigned yet. Click "Add Team Member" to start building your team.</p>
						</div>
					{:else}
						<div class="space-y-3">
							{#each form.audit_team as member, index}
								<div class="bg-surface-50 dark:bg-surface-800 border-2 border-surface-200 dark:border-surface-700 rounded-xl p-4">
									<div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-start">
										<!-- User Selection -->
										<div class="md:col-span-5">
											<label for="team-user-{index}" class="block text-xs font-semibold text-surface-700 dark:text-surface-300 mb-1">
												Team Member <span class="text-error-500">*</span>
											</label>
											<select
												id="team-user-{index}"
												onchange={(e) => {
													const value = (e.target as HTMLSelectElement).value;
													updateTeamMember(index, 'user_id', value);
												}}
												required
												disabled={!users || users.length === 0}
												class="w-full px-3 py-2 text-sm border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
											>
												<option value="0" selected={member.user_id === 0}>
													{#if !users || users.length === 0}
														Loading users...
													{:else}
														Select user...
													{/if}
												</option>
												{#if users && users.length > 0}
													{#each users as user}
														<option value={user.id} selected={member.user_id === user.id}>{user.username} ({user.email})</option>
													{/each}
												{/if}
											</select>
											{#if users && users.length === 0}
												<p class="text-xs text-warning-600 dark:text-warning-400 mt-1">
													⚠️ No users available. Please ensure users exist in the system.
												</p>
											{/if}
										</div>

										<!-- Role Selection -->
										<div class="md:col-span-5">
											<label for="team-role-{index}" class="block text-xs font-semibold text-surface-700 dark:text-surface-300 mb-1">
												Role <span class="text-error-500">*</span>
												{#if member.role === 'lead_auditor'}
													<span class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
														⭐ Lead
													</span>
												{/if}
											</label>
											<select
												id="team-role-{index}"
												onchange={(e) => {
													const value = (e.target as HTMLSelectElement).value;
													updateTeamMember(index, 'role', value);
												}}
												required
												class="w-full px-3 py-2 text-sm border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
											>
												{#each auditTeamRoles as role}
													<option value={role.value} selected={member.role === role.value}>
														{#if role.value === 'lead_auditor'}⭐ {/if}
														{role.label}
													</option>
												{/each}
											</select>
										</div>

										<!-- Remove Button -->
										<div class="md:col-span-2 flex items-end">
											<button
												type="button"
												onclick={() => removeTeamMember(index)}
												class="w-full md:w-auto px-3 py-2 text-sm font-semibold text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/20 rounded-lg transition-colors"
												title="Remove team member"
											>
												<svg class="w-4 h-4 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
												</svg>
											</button>
										</div>
									</div>
								</div>
							{/each}
						</div>

						<!-- Team Summary -->
						<div class="mt-4 p-3 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg">
							<div class="flex items-center gap-2 text-sm">
								<svg class="w-4 h-4 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<span class="text-primary-900 dark:text-primary-100">
									Team size: {form.audit_team.length} member{form.audit_team.length === 1 ? '' : 's'}
									{#if form.audit_team.some(m => m.role === 'lead_auditor')}
										<span class="text-primary-700 dark:text-primary-300">
											| ✓ Lead Auditor assigned
										</span>
									{:else}
										<span class="text-warning-700 dark:text-warning-300">
											| ⚠ No Lead Auditor assigned
										</span>
									{/if}
								</span>
							</div>
						</div>
					{/if}
				</div>
			</FormSection>

			<!-- Audit Details -->
			<FormSection title="🎯 Audit Details" subtitle="Define objectives and scope" collapsible={false}>
				<div class="space-y-6">
					<!-- Objectives -->
					<div>
						<label for="objectives" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
							</svg>
							Objectives
						</label>
						<textarea
							id="objectives"
							bind:value={form.objectives}
							rows="5"
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
							placeholder="• List the primary objectives of this audit&#10;• What are the key questions to answer?&#10;• What outcomes are expected?"
						></textarea>
					</div>

					<!-- Scope -->
					<div>
						<label for="scope" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
							<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
							Scope
						</label>
						<textarea
							id="scope"
							bind:value={form.scope}
							rows="5"
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
							placeholder="• Define what is included in this audit&#10;• Specify areas, processes, or systems to review&#10;• Note any exclusions or limitations"
						></textarea>
					</div>
				</div>
			</FormSection>

			<!-- Actions -->
			<div class="sticky bottom-0 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-900 dark:to-surface-800 border-t-2 border-surface-200 dark:border-surface-700 p-6 rounded-xl shadow-xl mt-8">
				<div class="flex justify-end gap-3">
					<button
						type="button"
						onclick={resetForm}
						class="px-6 py-3 border-2 border-surface-300 dark:border-surface-600 rounded-xl shadow-sm text-sm font-semibold text-surface-700 dark:text-surface-200 bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all flex items-center gap-2"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
						</svg>
						Reset
					</button>
					<button
						type="submit"
						disabled={saving}
						class="px-6 py-3 border-2 border-transparent rounded-xl shadow-lg text-sm font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 min-w-[140px] justify-center"
					>
						{#if saving}
							<svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							Saving...
						{:else}
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
							</svg>
							{planId ? 'Update Plan' : 'Create Plan'}
						{/if}
					</button>
				</div>
			</div>
		</form>
	{/if}
</div>
