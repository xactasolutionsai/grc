<script lang="ts">
    import {onMount} from 'svelte';
    import {page} from '$app/stores';
    import {pageTitle} from '$lib/utils/stores';
    import {breadcrumbs} from '$lib/utils/breadcrumbs';
    import {getEntity, getRelatedEntities, updateEntity, uploadOrgStructure, getHierarchy} from '../api.js';
    import {getUsers} from '../users-api.js';
	import HierarchyNode from '../HierarchyNode.svelte';
    import {
        listProcesses,
        createProcess,
        updateProcess as apiUpdateProcess,
        deleteProcess as apiDeleteProcess,
        uploadProcessesCSV,
        getProcessesLookup
    } from '../api.js';
    import EnhancedModal from '$lib/components/Modals/EnhancedModal.svelte';
    import FormSection from '../FormSection.svelte';

	export let entityId: string;

	let entity: any = null;
	let relatedEntities: any = null;
	let users: any[] = [];
	let loading = true;
	let error: string | null = null;
	let showEditModal = false;
	let editing = false;
	let editForm: any = {};
	let uploading = false;
	let uploadError: string | null = null;
	let hierarchy: any[] = [];
	let hierarchyLoading = false;
	let showFullHierarchy = false;
	let processes: any[] = [];
	let processesLoading = false;
    let processForm = {name: '', description: '', identifier: '', depends_on_id: null};
	let processSaving = false;
	let processesUploadMessage: string | null = null;
	let processesUploadErrors: string[] = [];
	let showProcessModal = false;
	let processesLookup: any[] = [];
	let processesLookupLoading = false;

	// Calculate risk reduction reactively
	$: riskReduction = entity
		? (entity.inherent_risk_score || 0) - (entity.residual_risk_score || 0)
		: 0;

	onMount(async () => {
		loadEntity();
		
		// Load users for owner dropdowns
		try {
			const data = await getUsers();
			users = data.results || data;
		} catch (err: any) {
			console.error('Error loading users for owner dropdowns:', err);
		}
	});

	// Watch for entityId changes
	$: if (entityId) {
		loadEntity();
	}

	async function loadEntity() {
		try {
			loading = true;
			error = null;
			
			// Fetch both entity details and related entities in parallel
			const [entityData, relatedData] = await Promise.all([
				getEntity(entityId),
				getRelatedEntities(entityId)
			]);
			
			entity = entityData;
			// Update page title and breadcrumbs when entity is loaded
			$pageTitle = entity?.name || '';
			if (entity?.name) {
				breadcrumbs.replace([
                    {label: 'Audit Universe', href: '/audits/universe'},
                    {label: entity.name, href: $page.url.pathname}
				]);
			}
			relatedEntities = relatedData;
		} catch (err: any) {
			console.error('Error loading entity:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	}

	function formatDate(dateString: string | null) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleDateString();
	}

	function formatDateTime(dateString: string | null) {
		if (!dateString) return '—';
		return new Date(dateString).toLocaleString();
	}

	function formatRegulatoryRelevance(relevance: any) {
		if (!relevance || typeof relevance !== 'object') return '—';
		return Object.entries(relevance)
			.filter(([_, value]) => value)
			.map(([key, _]) => key)
			.join(', ') || '—';
	}

	function openEditModal() {
		editForm = {
			name: entity.name || '',
			entity_type: entity.entity_type || 'process',
			description: entity.description || '',
			objectives: entity.objectives || '',
			parent: entity.parent || null,
			owner: entity.owner || null,
			contact_type: entity.contact_type || 'owner',
			key_contact: entity.key_contact || null,
			risk_score: entity.risk_score || 0,
			inherent_risk_score: entity.inherent_risk_score || null,
			residual_risk_score: entity.residual_risk_score || null,
			control_maturity: entity.control_maturity || null,
			regulatory_relevance: entity.regulatory_relevance || {},
			last_audited: entity.last_audited || '',
			criticality: entity.criticality || 'Medium',
			priority: entity.priority || 'medium',
			audit_frequency: entity.audit_frequency || 'Annual',
			next_audit_date: entity.next_audit_date || '',
			location: entity.location || '',
			country: entity.country || '',
			region: entity.region || '',
			city: entity.city || '',
			address: entity.address || '',
			postal_code: entity.postal_code || '',
			timezone: entity.timezone || '',
			coordinates: entity.coordinates || null,
			notes: entity.notes || '',
			is_active: entity.is_active !== undefined ? entity.is_active : true
		};
		showEditModal = true;
	}

	function closeEditModal() {
		showEditModal = false;
		editForm = {};
	}

	function viewInCalendar(dateString: string) {
		const date = new Date(dateString);
		const year = date.getFullYear();
		const month = date.getMonth() + 1; // JavaScript months are 0-based
		window.location.href = `/calendar/${year}/${month}`;
	}

	async function saveEntity() {
		try {
			editing = true;
			// Send complete editForm data for PUT request
			const updatedEntity = await updateEntity(entity.id, editForm);
			entity = updatedEntity;
			closeEditModal();
		} catch (err: any) {
			console.error('Error updating entity:', err);
			alert('Failed to update entity: ' + err.message);
		} finally {
			editing = false;
		}
	}

	async function onOrgStructureSelected(e: Event) {
		const input = e.currentTarget as HTMLInputElement;
		const file = input.files && input.files[0];
		if (!file || !entity?.id) return;
		uploadError = null;
		uploading = true;
		try {
			await uploadOrgStructure(entity.id, file);
			// refresh entity to get latest URL
			entity = await getEntity(entity.id);
		} catch (err: any) {
			uploadError = err.message;
		} finally {
			uploading = false;
			(input as HTMLInputElement).value = '';
		}
	}

	async function loadHierarchy() {
		try {
			hierarchyLoading = true;
			hierarchy = await getHierarchy();
		} catch (err: any) {
			console.error('Error loading hierarchy:', err);
		} finally {
			hierarchyLoading = false;
		}
	}

	function findEntityInHierarchy(hierarchy: any[], entityId: number): any {
		for (const node of hierarchy) {
			if (node.id === entityId) {
				return node;
			}
			if (node.children && node.children.length > 0) {
				const found = findEntityInHierarchy(node.children, entityId);
				if (found) return found;
			}
		}
		return null;
	}

	function getEntityPath(hierarchy: any[], entityId: number, path: any[] = []): any[] {
		for (const node of hierarchy) {
			const currentPath = [...path, node];
			if (node.id === entityId) {
				return currentPath;
			}
			if (node.children && node.children.length > 0) {
				const found = getEntityPath(node.children, entityId, currentPath);
				if (found.length > 0) return found;
			}
		}
		return [];
	}

	function formatEntityType(type: string) {
		return type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
	}

	function getEntityTypeColor(type: string) {
		const colors: Record<string, string> = {
			'business_unit': 'bg-blue-100 text-blue-800',
			'division': 'bg-green-100 text-green-800',
			'function': 'bg-purple-100 text-purple-800',
			'section': 'bg-yellow-100 text-yellow-800',
			'unit': 'bg-orange-100 text-orange-800',
			'process': 'bg-red-100 text-red-800',
			'system': 'bg-indigo-100 text-indigo-800',
			'vendor': 'bg-pink-100 text-pink-800',
			'compliance_domain': 'bg-gray-100 text-gray-800'
		};
		return colors[type] || 'bg-gray-100 text-gray-800';
	}

	async function loadProcesses() {
		if (!entity?.id) return;
		processesLoading = true;
		try {
			processes = await listProcesses(entity.id);
		} catch (e) {
			console.error('Failed to load processes', e);
		} finally {
			processesLoading = false;
		}
	}

	async function loadProcessesLookup() {
		processesLookupLoading = true;
		try {
			processesLookup = await getProcessesLookup();
		} catch (e: any) {
			console.error('Failed to load processes lookup', e);
		} finally {
			processesLookupLoading = false;
		}
	}

	function openProcessModal() {
        processForm = {name: '', description: '', identifier: '', depends_on_id: null};
		showProcessModal = true;
		loadProcessesLookup();
	}

	function closeProcessModal() {
		showProcessModal = false;
        processForm = {name: '', description: '', identifier: '', depends_on_id: null};
	}

	async function addProcess() {
		if (!entity?.id || !processForm.name.trim()) return;
		processSaving = true;
		try {
			await createProcess(entity.id, { 
				name: processForm.name.trim(), 
				description: processForm.description || '', 
				identifier: (processForm.identifier || '').trim(),
				depends_on_id: processForm.depends_on_id
			});
			closeProcessModal();
			await loadProcesses();
		} catch (e: any) {
			console.error('Failed to create process', e);
			alert(e?.message || 'Failed to create process');
		} finally {
			processSaving = false;
		}
	}

	async function editProcess(proc: any) {
		const identifier = prompt('Edit identifier', proc.identifier || '') ?? '';
		const name = prompt('Edit name', proc.name) ?? proc.name;
		const description = prompt('Edit description', proc.description || '') ?? '';
		try {
            await apiUpdateProcess(entity.id, proc.id, {identifier: identifier.trim(), name: name.trim(), description});
			await loadProcesses();
		} catch (e: any) {
			console.error('Failed to update process', e);
			alert(e?.message || 'Failed to update process');
		}
	}

	async function deleteProcess(proc: any) {
		if (!confirm(`Delete process/activity "${proc.name}"?`)) return;
		try {
			await apiDeleteProcess(entity.id, proc.id);
			await loadProcesses();
		} catch (e) {
			console.error('Failed to delete process', e);
		}
	}

	async function onProcessesCSVSelected(e: Event) {
		const input = e.currentTarget as HTMLInputElement;
		const file = input.files && input.files[0];
		if (!file || !entity?.id) return;
		processesUploadMessage = null;
		processesUploadErrors = [];
		try {
			const res = await uploadProcessesCSV(entity.id, file);
			processesUploadMessage = res.message || 'Upload complete';
			processesUploadErrors = res.errors || [];
			await loadProcesses();
		} catch (err: any) {
			processesUploadMessage = err.message || 'Upload failed';
		} finally {
			(input as HTMLInputElement).value = '';
		}
	}
</script>

{#if loading}
    <div class="flex justify-center items-center py-16">
        <div class="flex flex-col items-center gap-3">
            <svg class="animate-spin h-10 w-10 text-primary-600" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <div class="text-surface-600 dark:text-surface-400 font-medium">Loading entity details...</div>
        </div>
	</div>
{:else if error}
    <div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-6 flex items-start gap-3">
        <svg class="h-6 w-6 text-error-600 dark:text-error-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24"
             stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <div class="flex-1">
            <div class="text-error-800 dark:text-error-200 font-medium mb-3">Error: {error}</div>
		<button 
			onclick={loadEntity}
                    class="px-4 py-2 bg-error-600 hover:bg-error-700 text-white rounded-lg shadow-sm transition-colors flex items-center gap-2"
		>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
			Retry
		</button>
        </div>
	</div>
{:else if entity}
    <div class="mx-auto p-6">
        <!-- Header Card -->
        <div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 shadow-xl rounded-xl mb-8 overflow-hidden">
            <div class="px-8 py-6">
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <!-- Entity Type Icon & Badge -->
                        <div class="flex items-center gap-3 mb-3">
                            <div class="text-4xl">
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
					</div>
					<div>
                                <h1 class="text-3xl font-bold text-white">{entity.name}</h1>
                                <div class="mt-2 flex items-center gap-2 flex-wrap">
									<span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold bg-white/20 text-white backdrop-blur-sm">
								{formatEntityType(entity.entity_type)}
							</span>
                                    <span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold {entity.is_active ? 'bg-green-500/90 text-white' : 'bg-red-500/90 text-white'}">
										{entity.is_active ? '✅ Active' : '⏸️ Inactive'}
							</span>
                                    {#if entity.priority}
										<span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold {entity.priority === 'critical' ? 'bg-red-500/90' : entity.priority === 'high' ? 'bg-orange-500/90' : entity.priority === 'medium' ? 'bg-yellow-500/90' : 'bg-green-500/90'} text-white">
											{entity.priority === 'critical' ? '🔴' : entity.priority === 'high' ? '🟠' : entity.priority === 'medium' ? '🟡' : '🟢'} {entity.priority.charAt(0).toUpperCase() + entity.priority.slice(1)}
										</span>
                                    {/if}
						</div>
					</div>
					</div>
                        {#if entity.description}
                            <p class="text-white/90 text-sm max-w-2xl">{entity.description}</p>
                        {/if}
                    </div>

                    <!-- Risk Score Display -->
                    <div class="text-right bg-white/10 backdrop-blur-sm rounded-xl px-6 py-4">
                        <div class="text-sm text-white/80 font-medium mb-1">Risk Score</div>
                        <div class="text-4xl font-bold text-white">{entity.risk_score || '—'}</div>
                        <div class="text-xs text-white/70 mt-1">out of 10</div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="mt-6 flex items-center gap-3 flex-wrap">
                    <button
                            onclick={openEditModal}
                            class="px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-lg text-sm font-medium transition-all flex items-center gap-2 border border-white/20"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                        </svg>
                        Edit Entity
                    </button>
                    <a
                            href="/audits/planning/new?entity={entity.id}"
                            class="px-4 py-2 bg-white text-primary-700 hover:bg-white/90 rounded-lg text-sm font-semibold transition-all flex items-center gap-2"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                        </svg>
                        Plan Audit
                    </a>
                    {#if entity.next_audit_date}
                        <button
                                onclick={() => viewInCalendar(entity.next_audit_date)}
                                class="px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-lg text-sm font-medium transition-all flex items-center gap-2 border border-white/20"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                            </svg>
                            View in Calendar
                        </button>
                    {/if}
				</div>
			</div>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Main Content -->
			<div class="lg:col-span-2 space-y-6">
				<!-- Basic Information -->
                <div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                    <div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
                        <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            Basic Information
                        </h2>
					</div>
					<div class="px-6 py-4">
						<dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
							<div>
								<dt class="text-sm font-medium text-surface-500">Name</dt>
								<dd class="mt-1 text-sm text-surface-900">{entity.name}</dd>
							</div>
							<div>
								<dt class="text-sm font-medium text-surface-500">Entity Type</dt>
								<dd class="mt-1 text-sm text-surface-900">{formatEntityType(entity.entity_type)}</dd>
							</div>
							<div class="sm:col-span-2">
								<dt class="text-sm font-medium text-surface-500">Description</dt>
								<dd class="mt-1 text-sm text-surface-900">{entity.description || '—'}</dd>
							</div>
							<div class="sm:col-span-2">
								<dt class="text-sm font-medium text-surface-500">Objectives</dt>
								<dd class="mt-1 text-sm text-surface-900">
									{#if entity.objectives}
										<div class="bg-gray-50 rounded-md p-3 border border-surface-200">
											<div class="whitespace-pre-wrap text-sm text-surface-700">{entity.objectives}</div>
										</div>
									{:else}
										<span class="text-sm text-surface-500">No objectives provided.</span>
									{/if}
								</dd>
							</div>
						</dl>
					</div>
				</div>

				<!-- Processes / Activities -->
                <div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                    <div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700 flex items-center justify-between">
                        <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"/>
                            </svg>
                            Processes / Activities
                        </h2>
                        <div class="flex items-center gap-2">
                            <label class="px-3 py-2 text-xs font-medium rounded-lg border border-primary-300 dark:border-primary-600 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 cursor-pointer hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                                </svg>
                                <input type="file" accept=".csv" class="hidden" oninput={onProcessesCSVSelected}/>
								Upload CSV
							</label>
						</div>
					</div>
					<div class="px-6 py-4 space-y-4">
						{#if processesUploadMessage}
							<div class="text-sm text-surface-700">{processesUploadMessage}</div>
							{#if processesUploadErrors && processesUploadErrors.length}
								<ul class="list-disc ml-6 text-xs text-error-700">
									{#each processesUploadErrors as err}
										<li>{err}</li>
									{/each}
								</ul>
							{/if}
						{/if}

						<!-- Add button -->
						<div class="mb-4">
							<button 
                                    class="px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg shadow-sm transition-all font-medium flex items-center gap-2"
								onclick={openProcessModal}
							>
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                          d="M12 4v16m8-8H4"/>
                                </svg>
                                Add Process/Activity
							</button>
						</div>

						<!-- List -->
						{#if processesLoading}
							<div class="text-surface-600">Loading…</div>
						{:else if processes.length === 0}
							<div class="text-surface-500 text-sm">No processes/activities defined.</div>
						{:else}
							<table class="min-w-full text-sm">
								<thead>
									<tr class="text-left text-surface-500">
										<th class="py-2 pr-4">Name</th>
										<th class="py-2 pr-4">Description</th>
										<th class="py-2 pr-4">Depends On</th>
										<th class="py-2 pr-4">Actions</th>
									</tr>
								</thead>
								<tbody>
									{#each processes as p}
										<tr class="border-t border-surface-200">
											<td class="py-2 pr-4 font-medium">{p.identifier ? `${p.identifier} | ${p.name}` : p.name}</td>
											<td class="py-2 pr-4 whitespace-pre-wrap">{p.description}</td>
											<td class="py-2 pr-4">
												{#if p.depends_on}
													<span class="text-sm text-surface-600">
														{p.depends_on.identifier} – {p.depends_on.name}
                                                        ({p.depends_on.entity_name})
													</span>
												{:else}
													<span class="text-sm text-surface-400">No dependency</span>
												{/if}
											</td>
											<td class="py-2 pr-4 space-x-2">
                                            <button class="text-primary-600" onclick={() => editProcess(p)}>Edit
                                            </button>
                                            <button class="text-error-600" onclick={() => deleteProcess(p)}>Delete
                                            </button>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						{/if}
					</div>
				</div>

				<!-- Hierarchy Information -->
                <div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                    <div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
                        <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                            </svg>
                            Hierarchy
                        </h2>
					</div>
					<div class="px-6 py-4">
						<dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
							<div>
								<dt class="text-sm font-medium text-surface-500">Parent Entity</dt>
								<dd class="mt-1 text-sm text-surface-900">
									{#if entity.parent_name}
                                        <a href="/audits/universe/{entity.parent}"
                                           class="text-primary-600 hover:text-primary-800">
											{entity.parent_name}
										</a>
									{:else}
										—
									{/if}
								</dd>
							</div>
							<div>
								<dt class="text-sm font-medium text-surface-500">Children Entities</dt>
								<dd class="mt-1 text-sm text-surface-900">
									{#if entity.children && entity.children.length > 0}
										<ul class="space-y-1">
											{#each entity.children as child}
												<li>
                                                    <a href="/audits/universe/{child.id}"
                                                       class="text-primary-600 hover:text-primary-800">
														{child.name}
													</a>
												</li>
											{/each}
										</ul>
									{:else}
										—
									{/if}
								</dd>
							</div>
						</dl>
					</div>
				</div>

				<!-- Related Objects -->
                <div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                    <div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
                        <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
                            </svg>
                            Related Objects
                        </h2>
					</div>
					<div class="px-6 py-4">
						{#if relatedEntities}
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<!-- Engagements -->
								<div>
									<h3 class="text-sm font-medium text-surface-700 mb-2">Engagements</h3>
									{#if relatedEntities.engagements && relatedEntities.engagements.length > 0}
										<ul class="space-y-1">
											{#each relatedEntities.engagements as engagement}
												<li class="text-sm text-gray-600">
													{engagement.title} ({engagement.status})
												</li>
											{/each}
										</ul>
									{:else}
										<p class="text-sm text-surface-500">No engagements found</p>
									{/if}
								</div>

								<!-- Compliance Audits -->
								<div>
									<h3 class="text-sm font-medium text-surface-700 mb-2">Compliance Audits</h3>
									{#if relatedEntities.compliance_audits && relatedEntities.compliance_audits.length > 0}
										<ul class="space-y-1">
											{#each relatedEntities.compliance_audits as audit}
												<li class="text-sm text-gray-600">
													{audit.name} ({audit.framework})
												</li>
											{/each}
										</ul>
									{:else}
										<p class="text-sm text-surface-500">No compliance audits found</p>
									{/if}
								</div>

								<!-- Risks -->
								<div>
									<h3 class="text-sm font-medium text-surface-700 mb-2">Risks</h3>
									{#if relatedEntities.risks && relatedEntities.risks.length > 0}
										<ul class="space-y-1">
											{#each relatedEntities.risks as risk}
												<li class="text-sm text-gray-600">
													{risk.name} (Severity: {risk.severity})
												</li>
											{/each}
										</ul>
									{:else}
										<p class="text-sm text-surface-500">No risks found</p>
									{/if}
								</div>

								<!-- Controls -->
								<div>
									<h3 class="text-sm font-medium text-surface-700 mb-2">Controls</h3>
									{#if relatedEntities.controls && relatedEntities.controls.length > 0}
										<ul class="space-y-1">
											{#each relatedEntities.controls as control}
												<li class="text-sm text-gray-600">
													{control.name} ({control.status})
												</li>
											{/each}
										</ul>
									{:else}
										<p class="text-sm text-surface-500">No controls found</p>
									{/if}
								</div>
							</div>
						{:else}
							<div class="text-sm text-surface-500">
								<p>Loading related objects...</p>
							</div>
						{/if}
					</div>
				</div>

                <!-- Organizational Structure -->
                <div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                    <div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700 flex items-center justify-between">
                        <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                            </svg>
                            Organizational Structure
                        </h2>
                        <div class="flex items-center gap-2">
                            <button
                                    onclick={() => {
										showFullHierarchy = !showFullHierarchy;
										if (showFullHierarchy && hierarchy.length === 0) {
											loadHierarchy();
										}
									}}
                                    class="px-3 py-2 text-xs font-medium rounded-lg border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 hover:bg-surface-50 dark:hover:bg-surface-700 transition-colors flex items-center gap-2"
                            >
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="{showFullHierarchy ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'}" />
                                </svg>
                                {showFullHierarchy ? 'Hide' : 'Show'} Full Hierarchy
                            </button>
                            <label class="px-3 py-2 text-xs font-medium rounded-lg border border-primary-300 dark:border-primary-600 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 cursor-pointer hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                                </svg>
                                <input type="file" accept=".pdf,.png,.jpg,.jpeg,.svg" class="hidden"
                                       oninput={onOrgStructureSelected}/>
                                {uploading ? 'Uploading…' : 'Upload File'}
                            </label>
                        </div>
                    </div>
                    <div class="px-6 py-4 space-y-4">
                        {#if uploadError}
                            <div class="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-lg p-4 mb-4 flex items-start gap-3">
                                <svg class="h-5 w-5 text-error-600 dark:text-error-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <div class="text-error-800 dark:text-error-200 text-sm">{uploadError}</div>
                            </div>
                        {/if}

                        <!-- File Upload Section -->
                        {#if entity.org_structure_url}
                            <div class="mb-6">
                                <h3 class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-3 flex items-center gap-2">
                                    <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                    </svg>
                                    Uploaded Structure File
                                </h3>
                                <div class="bg-surface-50 dark:bg-surface-900/50 border border-surface-200 dark:border-surface-700 rounded-lg p-4">
                                    <a class="text-primary-600 hover:text-primary-800 dark:hover:text-primary-400 font-medium flex items-center gap-2" href={entity.org_structure_url} target="_blank" rel="noopener noreferrer">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                        </svg>
                                        View current file
                                    </a>
                                    {#if entity.org_structure_url.endsWith('.png') || entity.org_structure_url.endsWith('.jpg') || entity.org_structure_url.endsWith('.jpeg') || entity.org_structure_url.endsWith('.svg')}
                                        <img src={entity.org_structure_url} alt="Organizational structure" class="max-w-full rounded-lg border border-surface-200 dark:border-surface-700 mt-4 shadow-sm" />
                                    {:else if entity.org_structure_url.endsWith('.pdf')}
                                        <iframe src={entity.org_structure_url} class="w-full h-[600px] border border-surface-200 dark:border-surface-700 rounded-lg mt-4 shadow-sm" title="Organizational Structure PDF"></iframe>
                                    {/if}
                                </div>
                            </div>
                        {/if}

                        <!-- Hierarchy Section -->
                        <div class="border-t border-surface-200 dark:border-surface-700 pt-6">
                            <h3 class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-4 flex items-center gap-2">
                                <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                </svg>
                                Position in Organizational Hierarchy
                            </h3>

                            {#if showFullHierarchy}
                                {#if hierarchyLoading}
                                    <div class="flex justify-center items-center py-8">
                                        <div class="flex flex-col items-center gap-3">
                                            <svg class="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
                                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                            <div class="text-surface-600 dark:text-surface-400 text-sm">Loading hierarchy...</div>
                                        </div>
                                    </div>
                                {:else if hierarchy.length > 0}
                                    <div class="bg-surface-50 dark:bg-surface-900/50 border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                                        <div class="space-y-2">
                                            {#each hierarchy as rootNode}
                                                <HierarchyNode {rootNode} currentEntityId={entity.id}/>
                                            {/each}
                                        </div>
                                    </div>
                                {:else}
                                    <div class="bg-surface-50 dark:bg-surface-900/50 border border-surface-200 dark:border-surface-700 rounded-lg p-6 text-center">
                                        <p class="text-sm text-surface-500 dark:text-surface-400">No organizational hierarchy found.</p>
                                    </div>
                                {/if}
                            {:else}
                                <!-- Show entity path only -->
                                {#if hierarchy.length > 0}
                                    {@const entityPath = getEntityPath(hierarchy, entity.id)}
                                    {#if entityPath.length > 0}
                                        <div class="bg-surface-50 dark:bg-surface-900/50 border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                                            <div class="space-y-3">
                                                {#each entityPath as pathNode, index}
                                                    <div class="flex items-center gap-3 {index > 0 ? 'ml-6' : ''}">
                                                        {#if index > 0}
                                                            <svg class="w-5 h-5 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                                            </svg>
                                                        {/if}
                                                        <a
                                                            href="/audits/universe/{pathNode.id}"
                                                            class="text-sm {pathNode.id === entity.id ? 'font-semibold text-primary-600 dark:text-primary-400' : 'text-surface-700 dark:text-surface-300 hover:text-primary-600 dark:hover:text-primary-400'} flex items-center gap-2"
                                                        >
                                                            <div class="text-xl">
                                                                {#if pathNode.entity_type === 'business_unit'}🏢
                                                                {:else if pathNode.entity_type === 'division'}🔷
                                                                {:else if pathNode.entity_type === 'function'}⚙️
                                                                {:else if pathNode.entity_type === 'section'}📑
                                                                {:else if pathNode.entity_type === 'unit'}📦
                                                                {:else if pathNode.entity_type === 'process'}🔄
                                                                {:else if pathNode.entity_type === 'system'}💻
                                                                {:else if pathNode.entity_type === 'vendor'}🤝
                                                                {:else if pathNode.entity_type === 'compliance_domain'}📋
                                                                {:else if pathNode.entity_type === 'audit_domain'}🎯
                                                                {:else}📄
                                                                {/if}
                                                            </div>
                                                            {pathNode.name}
                                                        </a>
                                                        <span class="inline-flex items-center px-2 py-0.5 rounded-lg text-xs font-medium bg-surface-100 dark:bg-surface-700 text-surface-700 dark:text-surface-300">
                                                            {formatEntityType(pathNode.entity_type)}
                                                        </span>
                                                    </div>
                                                {/each}
                                            </div>
                                        </div>
                                                    {:else}
                                        <div class="bg-surface-50 dark:bg-surface-900/50 border border-surface-200 dark:border-surface-700 rounded-lg p-6 text-center">
                                            <p class="text-sm text-surface-500 dark:text-surface-400">This entity is not part of the organizational hierarchy.</p>
                                        </div>
                                    {/if}
                                {:else}
                                    <div class="bg-surface-50 dark:bg-surface-900/50 border border-surface-200 dark:border-surface-700 rounded-lg p-6 text-center">
                                        <button
                                            onclick={loadHierarchy}
                                            class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2 mx-auto"
                                        >
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                            </svg>
                                            Load hierarchy to see position
                                        </button>
                                    </div>
                                {/if}
                            {/if}
                        </div>
                    </div>
                </div>
			</div>

			<!-- Sidebar -->
			<div class="space-y-6">
				<!-- Metadata -->
                <div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                    <div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
                        <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                            </svg>
                            Metadata
                        </h2>
					</div>
					<div class="px-6 py-4 space-y-4">
						<div>
							<dt class="text-sm font-medium text-surface-500">Contact Type</dt>
							<dd class="mt-1 text-sm text-surface-900">
								{entity.contact_type === 'owner' ? 'Owner' : 'Key Contact'}
							</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-surface-500">
								{entity.contact_type === 'owner' ? 'Owner' : 'Key Contact'}
							</dt>
							<dd class="mt-1 text-sm text-surface-900">
								{entity.contact_type === 'owner' ? (entity.owner_display || '—') : (entity.key_contact_display || '—')}
							</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-surface-500">Risk Score</dt>
							<dd class="mt-1 text-sm text-surface-900">{entity.risk_score || '—'}</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-surface-500">Last Audited</dt>
							<dd class="mt-1 text-sm text-surface-900">{formatDate(entity.last_audited)}</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-surface-500">Criticality</dt>
							<dd class="mt-1">
								{#if entity.criticality}
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {entity.criticality === 'High' ? 'bg-red-100 text-red-800' : entity.criticality === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}">
										{entity.criticality}
									</span>
								{:else}
									<span class="text-sm text-surface-500">—</span>
								{/if}
							</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-surface-500">Priority</dt>
							<dd class="mt-1">
								{#if entity.priority}
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {entity.priority === 'critical' ? 'bg-red-100 text-red-800' : entity.priority === 'high' ? 'bg-orange-100 text-orange-800' : entity.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}">
										{entity.priority.charAt(0).toUpperCase() + entity.priority.slice(1)}
									</span>
								{:else}
									<span class="text-sm text-surface-500">—</span>
								{/if}
							</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-surface-500">Audit Frequency</dt>
							<dd class="mt-1 text-sm text-surface-900">{entity.audit_frequency || '—'}</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-surface-500">Next Audit Date</dt>
							<dd class="mt-1 text-sm text-surface-900">{formatDate(entity.next_audit_date)}</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-surface-500">Regulatory Relevance</dt>
							<dd class="mt-1 text-sm text-surface-900">{formatRegulatoryRelevance(entity.regulatory_relevance)}</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-surface-500">Status</dt>
							<dd class="mt-1">
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {entity.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
									{entity.is_active ? 'Active' : 'Inactive'}
								</span>
							</dd>
						</div>
					</div>
				</div>

				<!-- Risk Assessment -->
                <div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                    <div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
                        <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                            </svg>
                            Risk Assessment
                        </h2>
					</div>
					<div class="px-6 py-4 space-y-4">
						<div>
							<dt class="text-sm font-medium text-surface-500">Overall Risk Score</dt>
							<dd class="mt-1">
								<div class="flex items-center">
									<div class="flex-1 bg-gray-200 rounded-full h-2 mr-3">
										<div 
											class="bg-blue-600 h-2 rounded-full transition-all duration-300"
											style="width: {((entity.risk_score || 0) / 10) * 100}%"
										></div>
									</div>
									<span class="text-sm font-medium text-surface-900 min-w-[3rem] text-right">
										{entity.risk_score || 0}/10
									</span>
								</div>
							</dd>
						</div>
						
						<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
							<div>
								<dt class="text-sm font-medium text-surface-500">Inherent Risk</dt>
								<dd class="mt-1">
									{#if entity.inherent_risk_score !== null}
										<div class="flex items-center">
											<div class="flex-1 bg-gray-200 rounded-full h-2 mr-3">
												<div 
													class="bg-red-500 h-2 rounded-full transition-all duration-300"
													style="width: {((entity.inherent_risk_score) / 10) * 100}%"
												></div>
											</div>
											<span class="text-sm font-medium text-surface-900 min-w-[3rem] text-right">
												{entity.inherent_risk_score}/10
											</span>
										</div>
									{:else}
										<span class="text-sm text-surface-500">Not assessed</span>
									{/if}
								</dd>
							</div>
							
							<div>
								<dt class="text-sm font-medium text-surface-500">Residual Risk</dt>
								<dd class="mt-1">
									{#if entity.residual_risk_score !== null}
										<div class="flex items-center">
											<div class="flex-1 bg-gray-200 rounded-full h-2 mr-3">
												<div 
													class="bg-orange-500 h-2 rounded-full transition-all duration-300"
													style="width: {((entity.residual_risk_score) / 10) * 100}%"
												></div>
											</div>
											<span class="text-sm font-medium text-surface-900 min-w-[3rem] text-right">
												{entity.residual_risk_score}/10
											</span>
										</div>
									{:else}
										<span class="text-sm text-surface-500">Not assessed</span>
									{/if}
								</dd>
							</div>
						</div>
						
						<div>
							<dt class="text-sm font-medium text-surface-500">Control Maturity</dt>
							<dd class="mt-1">
								{#if entity.control_maturity !== null}
									<div class="flex items-center">
										<div class="flex-1 bg-gray-200 rounded-full h-2 mr-3">
											<div 
												class="bg-green-500 h-2 rounded-full transition-all duration-300"
												style="width: {((entity.control_maturity) / 5) * 100}%"
											></div>
										</div>
										<span class="text-sm font-medium text-surface-900 min-w-[3rem] text-right">
											{entity.control_maturity}/5
										</span>
									</div>
									<div class="text-xs text-surface-500 mt-1">
										{entity.control_maturity === 0 && 'Initial - Ad hoc processes'}
										{entity.control_maturity === 1 && 'Managed - Basic processes in place'}
										{entity.control_maturity === 2 && 'Defined - Standardized processes'}
										{entity.control_maturity === 3 && 'Quantified - Measured and controlled'}
										{entity.control_maturity === 4 && 'Optimizing - Continuously improved'}
										{entity.control_maturity === 5 && 'Advanced - Best-in-class practices'}
									</div>
								{:else}
									<span class="text-sm text-surface-500">Not assessed</span>
								{/if}
							</dd>
						</div>
						
						{#if entity.inherent_risk_score !== null && entity.residual_risk_score !== null}
							<div class="pt-4 border-t border-surface-200">
								<dt class="text-sm font-medium text-surface-500">Risk Reduction</dt>
								<dd class="mt-1">
									<div class="flex items-center">
										<span class="text-sm font-medium {riskReduction > 0 ? 'text-green-600' : riskReduction < 0 ? 'text-red-600' : 'text-gray-600'}">
											{riskReduction > 0 ? '+' : ''}{riskReduction.toFixed(1)} points
										</span>
										<span class="ml-2 text-xs text-surface-500">
											{riskReduction > 0 ? 'Controls are effective' : riskReduction < 0 ? 'Risk increased' : 'No change'}
										</span>
									</div>
								</dd>
							</div>
						{/if}
					</div>
				</div>

				<!-- Geographical Location -->
                <div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                    <div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
                        <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            Geographical Location
                            <span class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200">New</span>
						</h2>
					</div>
					<div class="px-6 py-4 space-y-4">
						<!-- Full Location Display -->
						<div>
							<dt class="text-sm font-medium text-surface-500">Full Location</dt>
							<dd class="mt-1 text-sm text-surface-900">
								{#if entity.full_location}
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
										<svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
										</svg>
										{entity.full_location}
									</span>
								{:else if entity.location}
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
										<svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
										</svg>
										{entity.location} (Legacy)
									</span>
								{:else}
									<span class="text-sm text-surface-500">Not specified</span>
								{/if}
							</dd>
						</div>

						<!-- Detailed Location Information -->
						{#if entity.country || entity.region || entity.city}
							<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
								{#if entity.country}
									<div>
										<dt class="text-sm font-medium text-surface-500">Country</dt>
										<dd class="mt-1 text-sm text-surface-900">{entity.country}</dd>
									</div>
								{/if}
								{#if entity.region}
									<div>
										<dt class="text-sm font-medium text-surface-500">Region/State</dt>
										<dd class="mt-1 text-sm text-surface-900">{entity.region}</dd>
									</div>
								{/if}
								{#if entity.city}
									<div>
										<dt class="text-sm font-medium text-surface-500">City</dt>
										<dd class="mt-1 text-sm text-surface-900">{entity.city}</dd>
									</div>
								{/if}
							</div>
						{/if}

						<!-- Address -->
						{#if entity.address}
							<div>
								<dt class="text-sm font-medium text-surface-500">Address</dt>
								<dd class="mt-1 text-sm text-surface-900">
									<div class="bg-gray-50 rounded-md p-3 border border-surface-200">
										<div class="whitespace-pre-wrap">{entity.address}</div>
									</div>
								</dd>
							</div>
						{/if}

						<!-- Postal Code and Timezone -->
						{#if entity.postal_code || entity.timezone}
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								{#if entity.postal_code}
									<div>
										<dt class="text-sm font-medium text-surface-500">Postal Code</dt>
										<dd class="mt-1 text-sm text-surface-900">{entity.postal_code}</dd>
									</div>
								{/if}
								{#if entity.timezone}
									<div>
										<dt class="text-sm font-medium text-surface-500">Timezone</dt>
										<dd class="mt-1 text-sm text-surface-900">{entity.timezone}</dd>
									</div>
								{/if}
							</div>
						{/if}

						<!-- Coordinates -->
						{#if entity.coordinates && entity.coordinates.latitude && entity.coordinates.longitude}
							<div>
								<dt class="text-sm font-medium text-surface-500">Coordinates</dt>
								<dd class="mt-1 text-sm text-surface-900">
									<div class="flex items-center space-x-4">
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
											<svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor"
                                                 viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                      d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
											</svg>
                                            {entity.coordinates.latitude.toFixed(6)}
                                            , {entity.coordinates.longitude.toFixed(6)}
										</span>
										<a
											href="https://www.google.com/maps?q={entity.coordinates.latitude},{entity.coordinates.longitude}"
											target="_blank"
											rel="noopener noreferrer"
											class="text-primary-600 hover:text-primary-800 text-xs"
										>
											View on Google Maps
										</a>
									</div>
								</dd>
							</div>
						{/if}
					</div>
				</div>

                <!-- Additional Information -->
                <div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                    <div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
                        <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"/>
														</svg>
                            Additional Information
                        </h2>
					</div>
					<div class="px-6 py-4 space-y-4">
						<div>
							<dt class="text-sm font-medium text-surface-500">Notes</dt>
							<dd class="mt-1 text-sm text-surface-900">
								{#if entity.notes}
									<div class="bg-gray-50 rounded-md p-3 border border-surface-200">
										<div class="whitespace-pre-wrap text-sm text-surface-700">{entity.notes}</div>
									</div>
								{:else}
									<span class="text-sm text-surface-500">No notes available</span>
								{/if}
							</dd>
						</div>
					</div>
				</div>

				<!-- Timestamps -->
                <div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                    <div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
                        <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            Timestamps
                        </h2>
					</div>
					<div class="px-6 py-4 space-y-4">
						<div>
							<dt class="text-sm font-medium text-surface-500">Created At</dt>
							<dd class="mt-1 text-sm text-surface-900">{formatDateTime(entity.created_at)}</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-surface-500">Updated At</dt>
							<dd class="mt-1 text-sm text-surface-900">{formatDateTime(entity.updated_at)}</dd>
						</div>
					</div>
				</div>

				<!-- Actions -->
                <div class="bg-white dark:bg-surface-800 shadow-lg rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                    <div class="px-6 py-4 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-900 border-b border-surface-200 dark:border-surface-700">
                        <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-50 flex items-center gap-2">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M13 10V3L4 14h7v7l9-11h-7z"/>
                            </svg>
                            Quick Actions
                        </h2>
					</div>
					<div class="px-6 py-4 space-y-3">
						<a
							href="/audits/planning/new?entity={entity.id}"
                                class="w-full inline-flex justify-center items-center gap-2 px-5 py-2.5 border border-transparent shadow-sm text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
						>
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                            </svg>
							Plan Audit
						</a>
						<button
							onclick={openEditModal}
                                class="w-full inline-flex justify-center items-center gap-2 px-5 py-2.5 border border-surface-300 dark:border-surface-600 shadow-sm text-sm font-medium rounded-lg text-surface-700 dark:text-surface-300 bg-white dark:bg-surface-900 hover:bg-surface-50 dark:hover:bg-surface-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
						>
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                            </svg>
							Edit Entity
						</button>
						{#if entity.next_audit_date}
							<button
								onclick={() => viewInCalendar(entity.next_audit_date)}
                                    class="w-full inline-flex justify-center items-center gap-2 px-5 py-2.5 border border-surface-300 dark:border-surface-600 shadow-sm text-sm font-medium rounded-lg text-surface-700 dark:text-surface-300 bg-white dark:bg-surface-900 hover:bg-surface-50 dark:hover:bg-surface-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
							>
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                                </svg>
								View in Calendar
							</button>
						{/if}
						<button
							onclick={() => {
								if (confirm(`Are you sure you want to delete "${entity.name}"? This action cannot be undone.`)) {
									// TODO: Implement delete functionality
									alert('Delete functionality will be implemented');
								}
							}}
                                class="w-full inline-flex justify-center items-center gap-2 px-5 py-2.5 border border-transparent shadow-sm text-sm font-medium rounded-lg text-white bg-error-600 hover:bg-error-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-error-500 transition-all"
						>
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                            </svg>
							Delete Entity
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div class="max-w-6xl mx-auto p-6">
		<div class="bg-surface-50 shadow rounded-lg">
			<div class="px-6 py-8 text-center">
				<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.29-1.009-5.824-2.709M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
				</svg>
				<h3 class="mt-2 text-sm font-medium text-surface-900">Entity not found</h3>
                <p class="mt-1 text-sm text-surface-500">The audit entity you're looking for doesn't exist or has been
                    removed.</p>
				<div class="mt-6">
					<a
						href="/audits/universe"
						class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
					>
						<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
						</svg>
						Back to Audit Universe
					</a>
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- Edit Modal -->
<EnhancedModal
        bind:open={showEditModal}
        title="Edit Entity"
        maxWidth="4xl"
        onClose={closeEditModal}
>
    <div class="enhanced-modal-body">
        <form onsubmit={(e) => { e.preventDefault(); saveEntity(); }} class="space-y-4">
            <!-- Basic Information Section -->
            <FormSection title="Basic Information">
                <div class="space-y-4">
					<div>
                        <label for="edit-name"
                               class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Name
                            <span class="text-error-500">*</span></label>
						<input
							id="edit-name"
							type="text"
							bind:value={editForm.name}
							required
                                class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							placeholder="Enter entity name"
						/>
					</div>
					
					<div>
                        <label for="edit-type"
                               class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Entity
                            Type <span class="text-error-500">*</span></label>
						<select
							id="edit-type"
							bind:value={editForm.entity_type}
							required
                                class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
                        >
                            <option value="business_unit">🏢 Business Unit</option>
                            <option value="division">🔷 Division</option>
                            <option value="function">⚙️ Function</option>
                            <option value="section">📑 Section</option>
                            <option value="unit">📦 Unit</option>
                            <option value="process">🔄 Process</option>
                            <option value="system">💻 System</option>
                            <option value="vendor">🤝 Vendor</option>
                            <option value="compliance_domain">📋 Compliance Domain</option>
                            <option value="audit_domain">🎯 Audit Domain</option>
						</select>
					</div>
					
					<div>
                        <label for="edit-description"
                               class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Description</label>
						<textarea
							id="edit-description"
							bind:value={editForm.description}
							rows="3"
                                class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
						></textarea>
					</div>

					<div>
                        <label for="edit-objectives"
                               class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Objectives</label>
						<textarea
							id="edit-objectives"
							bind:value={editForm.objectives}
                                rows="3"
                                class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
                                placeholder="Enter the objectives or responsibilities of this entity"
						></textarea>
					</div>
                </div>
            </FormSection>
					
					<!-- Contact Information Section -->
            <FormSection title="Contact Information" collapsible={true} defaultOpen={true}>
                <div class="space-y-4">
                    <div>
                        <label for="edit-contact-type"
                               class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Contact
                            Type</label>
							<select
								id="edit-contact-type"
								bind:value={editForm.contact_type}
                                class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							>
								<option value="owner">Owner</option>
								<option value="key_contact">Key Contact</option>
							</select>
						</div>

						{#if editForm.contact_type === 'owner'}
							<div>
                            <label for="edit-owner"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Owner</label>
								<select
									id="edit-owner"
									bind:value={editForm.owner}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
								>
									<option value="">Select owner (optional)</option>
									{#each users as user}
										<option value={user.id}>{user.username} ({user.email})</option>
									{/each}
								</select>
							</div>
						{:else}
							<div>
                            <label for="edit-key-contact"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Key
                                Contact</label>
								<select
									id="edit-key-contact"
									bind:value={editForm.key_contact}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
								>
									<option value="">Select key contact (optional)</option>
									{#each users as user}
										<option value={user.id}>{user.username} ({user.email})</option>
									{/each}
								</select>
							</div>
						{/if}
					</div>
            </FormSection>
					
            <!-- Risk Assessment Section -->
            <FormSection title="Risk Assessment" collapsible={true} defaultOpen={false}>
                <div class="space-y-4">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
                            <label for="edit-risk-score"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Overall
                                Risk Score</label>
							<input
								id="edit-risk-score"
								type="number"
								min="0"
								max="10"
								step="0.1"
								bind:value={editForm.risk_score}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
								placeholder="0-10"
							/>
						</div>
						
						<div>
                            <label for="edit-inherent-risk-score"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Inherent
                                Risk Score</label>
							<input
								id="edit-inherent-risk-score"
								type="number"
								min="0"
								max="10"
								step="0.1"
								bind:value={editForm.inherent_risk_score}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
								placeholder="0-10"
							/>
						</div>
					</div>
					
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
                            <label for="edit-residual-risk-score"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Residual
                                Risk Score</label>
							<input
								id="edit-residual-risk-score"
								type="number"
								min="0"
								max="10"
								step="0.1"
								bind:value={editForm.residual_risk_score}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
								placeholder="0-10"
							/>
						</div>
						
						<div>
                            <label for="edit-control-maturity"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Control
                                Maturity Level</label>
                            <div class="flex items-center gap-3 mt-1">
								<input
									id="edit-control-maturity"
									type="range"
									min="0"
									max="5"
									step="1"
									bind:value={editForm.control_maturity}
                                        class="flex-1 h-2 bg-surface-200 dark:bg-surface-700 rounded-lg appearance-none cursor-pointer"
								/>
                                <span class="text-sm font-semibold text-surface-900 dark:text-surface-50 min-w-[2rem] text-center px-2 py-1 bg-surface-100 dark:bg-surface-800 rounded">
									{editForm.control_maturity || 0}
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
						</div>
            </FormSection>
						
            <!-- Audit Planning Section -->
            <FormSection title="Audit Planning" collapsible={true} defaultOpen={false}>
                <div class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
						<div>
                            <label for="edit-criticality"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Criticality</label>
							<select
								id="edit-criticality"
								bind:value={editForm.criticality}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							>
								<option value="High">High</option>
								<option value="Medium">Medium</option>
								<option value="Low">Low</option>
							</select>
						</div>
						
						<div>
                            <label for="edit-priority"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Priority</label>
							<select
								id="edit-priority"
								bind:value={editForm.priority}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							>
								<option value="low">Low</option>
								<option value="medium">Medium</option>
								<option value="high">High</option>
								<option value="critical">Critical</option>
							</select>
						</div>
						
						<div>
                            <label for="edit-audit-frequency"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Audit
                                Frequency</label>
							<select
								id="edit-audit-frequency"
								bind:value={editForm.audit_frequency}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							>
								<option value="annual">Annual</option>
								<option value="semiannual">Semi-annual</option>
								<option value="quarterly">Quarterly</option>
								<option value="monthly">Monthly</option>
								<option value="ad-hoc">Ad-hoc</option>
							</select>
						</div>
					</div>
					
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="edit-last-audited"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Last
                                Audited</label>
                            <input
                                    id="edit-last-audited"
                                    type="date"
                                    bind:value={editForm.last_audited}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
                            />
                        </div>

                        <div>
                            <label for="edit-next-audit-date"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Next
                                Audit Date</label>
                            <input
                                    id="edit-next-audit-date"
                                    type="date"
                                    bind:value={editForm.next_audit_date}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
                            />
                        </div>
                    </div>
                </div>
            </FormSection>

            <!-- Geographical Location Section -->
            <FormSection title="Geographical Location" badge="New" collapsible={true} defaultOpen={false}>
                <div class="space-y-4">
						<!-- Legacy location field -->
                    <div class="bg-surface-50 dark:bg-surface-800/50 border border-surface-200 dark:border-surface-700 rounded-lg p-3">
                        <label for="edit-location"
                               class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Legacy
                            Location <span class="text-xs text-surface-500">(Optional)</span></label>
							<input
								id="edit-location"
								type="text"
								bind:value={editForm.location}
                                class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
                                placeholder="Enter jurisdiction/region (e.g., US, EU, APAC)"
							/>
                        <p class="text-xs text-surface-500 dark:text-surface-400 mt-1">⚠️ For backward compatibility.
                            Use structured fields below.</p>
						</div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
							<div>
                            <label for="edit-country"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Country</label>
								<input
									id="edit-country"
									type="text"
									bind:value={editForm.country}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
									placeholder="e.g., United States"
								/>
							</div>
							
							<div>
                            <label for="edit-region"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Region/State</label>
								<input
									id="edit-region"
									type="text"
									bind:value={editForm.region}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
									placeholder="e.g., California"
								/>
							</div>
							
							<div>
                            <label for="edit-city"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">City</label>
								<input
									id="edit-city"
									type="text"
									bind:value={editForm.city}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
									placeholder="e.g., San Francisco"
								/>
							</div>
						</div>

                    <div>
                        <label for="edit-address"
                               class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Address</label>
							<textarea
								id="edit-address"
								bind:value={editForm.address}
								rows="2"
                                class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
								placeholder="Enter full physical address"
							></textarea>
						</div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
							<div>
                            <label for="edit-postal-code"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Postal/ZIP
                                Code</label>
								<input
									id="edit-postal-code"
									type="text"
									bind:value={editForm.postal_code}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
									placeholder="e.g., 94105"
								/>
							</div>
							
							<div>
                            <label for="edit-timezone"
                                   class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Timezone</label>
								<select
									id="edit-timezone"
									bind:value={editForm.timezone}
                                    class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
								>
									<option value="">Select timezone (optional)</option>
									<option value="UTC">UTC</option>
									<option value="America/New_York">America/New_York (EST/EDT)</option>
									<option value="America/Chicago">America/Chicago (CST/CDT)</option>
									<option value="America/Denver">America/Denver (MST/MDT)</option>
									<option value="America/Los_Angeles">America/Los_Angeles (PST/PDT)</option>
									<option value="Europe/London">Europe/London (GMT/BST)</option>
									<option value="Europe/Paris">Europe/Paris (CET/CEST)</option>
									<option value="Europe/Berlin">Europe/Berlin (CET/CEST)</option>
									<option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
									<option value="Asia/Shanghai">Asia/Shanghai (CST)</option>
									<option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
									<option value="Australia/Sydney">Australia/Sydney (AEST/AEDT)</option>
									<option value="Pacific/Auckland">Pacific/Auckland (NZST/NZDT)</option>
								</select>
							</div>
						</div>

						<!-- Coordinates -->
                    <div>
                        <span class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">Coordinates <span
                                class="text-xs text-surface-500">(Optional)</span></span>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div>
                                <label for="edit-latitude"
                                       class="block text-xs text-surface-600 dark:text-surface-400 mb-1">Latitude</label>
									<input
										id="edit-latitude"
										type="number"
										step="any"
										min="-90"
										max="90"
										value={editForm.coordinates?.latitude || ''}
								oninput={(e) => {
									const target = e.currentTarget as HTMLInputElement;
									const lat = parseFloat(target.value);
											const lng = editForm.coordinates?.longitude || null;
											if (!isNaN(lat) && lng !== null) {
												editForm.coordinates = { latitude: lat, longitude: lng };
											} else if (!isNaN(lat)) {
												editForm.coordinates = { latitude: lat, longitude: 0 };
											} else {
												editForm.coordinates = null;
											}
										}}
                                        class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
                                        placeholder="37.7749"
									/>
								</div>
								
								<div>
                                <label for="edit-longitude"
                                       class="block text-xs text-surface-600 dark:text-surface-400 mb-1">Longitude</label>
									<input
										id="edit-longitude"
										type="number"
										step="any"
										min="-180"
										max="180"
										value={editForm.coordinates?.longitude || ''}
								oninput={(e) => {
									const target = e.currentTarget as HTMLInputElement;
									const lng = parseFloat(target.value);
											const lat = editForm.coordinates?.latitude || null;
											if (!isNaN(lng) && lat !== null) {
												editForm.coordinates = { latitude: lat, longitude: lng };
											} else if (!isNaN(lng)) {
												editForm.coordinates = { latitude: 0, longitude: lng };
											} else {
												editForm.coordinates = null;
											}
										}}
                                        class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
                                        placeholder="-122.4194"
									/>
								</div>
							</div>
                        <p class="text-xs text-surface-500 dark:text-surface-400 mt-1.5">📍 Enter latitude (-90 to 90)
                            and longitude (-180 to 180).</p>
						</div>
					</div>
            </FormSection>
					
            <!-- Additional Information Section -->
            <FormSection title="Additional Information" collapsible={true} defaultOpen={false}>
                <div class="space-y-4">
					<div>
                        <label for="edit-notes"
                               class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Notes</label>
						<textarea
							id="edit-notes"
							bind:value={editForm.notes}
                                rows="3"
                                class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							placeholder="Enter additional notes and observations"
						></textarea>
					</div>
					
                    <div class="flex items-center gap-3 p-3 bg-surface-50 dark:bg-surface-800/50 rounded-lg">
						<input
							id="edit-active"
							type="checkbox"
							bind:checked={editForm.is_active}
                                class="h-4 w-4 text-primary-600 focus:ring-2 focus:ring-primary-500 border-surface-300 dark:border-surface-600 rounded"
						/>
                        <label for="edit-active"
                               class="text-sm font-medium text-surface-900 dark:text-surface-50 cursor-pointer select-none">
                            Active Entity
						</label>
					</div>
                </div>
            </FormSection>
					
            <!-- Form Actions -->
            <div class="flex justify-end gap-3 pt-4 sticky bottom-0 bg-white dark:bg-surface-900 border-t border-surface-200 dark:border-surface-700 -mx-6 px-6 py-4">
						<button
							type="button"
							onclick={closeEditModal}
                        class="px-5 py-2.5 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm text-sm font-medium text-surface-700 dark:text-surface-300 bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
						>
							Cancel
						</button>
						<button
							type="submit"
							disabled={editing}
                        class="px-5 py-2.5 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                    {#if editing}
                        <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor"
                                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Saving...
                    {:else}
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                        </svg>
                        Save Changes
                    {/if}
						</button>
					</div>
				</form>
			</div>
</EnhancedModal>

<!-- Process Modal -->
<EnhancedModal
        bind:open={showProcessModal}
        title="Add Process/Activity"
        maxWidth="lg"
        onClose={closeProcessModal}
>
				<form onsubmit={(e) => { e.preventDefault(); addProcess(); }}>
					<div class="space-y-4">
						<div>
                <label for="process-identifier"
                       class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
                    Identifier <span class="text-xs text-surface-500">(Auto-generated if blank)</span>
                </label>
							<input
								id="process-identifier"
								type="text"
								bind:value={processForm.identifier}
                        placeholder="e.g., PROC-001"
                        class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							/>
						</div>
						
						<div>
                <label for="process-name"
                       class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
                    Name <span class="text-error-500">*</span>
                </label>
							<input
								id="process-name"
								type="text"
								bind:value={processForm.name}
								placeholder="Process/Activity name"
								required
                        class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							/>
						</div>
						
						<div>
                <label for="process-description"
                       class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Description</label>
							<textarea
								id="process-description"
								bind:value={processForm.description}
								placeholder="Optional description"
								rows="3"
                        class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							></textarea>
						</div>
						
						<div>
                <label for="process-depends-on"
                       class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">Depends
                    On</label>
							<select
								id="process-depends-on"
								bind:value={processForm.depends_on_id}
                        class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900"
							>
								<option value={null}>No dependency</option>
								{#if processesLookupLoading}
									<option disabled>Loading...</option>
								{:else}
									{#each processesLookup as process}
										<option value={process.id}>{process.display_name}</option>
									{/each}
								{/if}
							</select>
						</div>
					</div>
					
        <div class="flex justify-end gap-3 pt-6 mt-6 border-t border-surface-200 dark:border-surface-700">
						<button
							type="button"
							onclick={closeProcessModal}
                    class="px-5 py-2.5 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm text-sm font-medium text-surface-700 dark:text-surface-300 bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
						>
							Cancel
						</button>
						<button
							type="submit"
							disabled={processSaving || !processForm.name.trim()}
                    class="px-5 py-2.5 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
                {#if processSaving}
                    <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Saving...
                {:else}
                    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                    </svg>
                    Add Process
                {/if}
						</button>
					</div>
				</form>
</EnhancedModal>

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
