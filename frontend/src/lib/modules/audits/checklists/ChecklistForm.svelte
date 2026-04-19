<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getChecklist, createChecklist, updateChecklist } from './api.js';

	interface Props {
		checklistId?: string;
	}

	let { checklistId }: Props = $props();

	let formData = $state({
		name: '',
		description: '',
		folder: null as string | null,
		status: 'draft' as string,
		is_published: true
	});

	let loading = $state(false);
	let error = $state('');
	let isEditMode = $state(false);
	let saving = $state(false);

	// Available folders - would load from API
	let availableFolders = $state<Array<{id: string, name: string}>>([]);
	let foldersLoading = $state(false);

	const statusChoices = [
		{ value: 'draft', label: '📝 Draft', description: 'Work in progress, not ready for use' },
		{ value: 'active', label: '✅ Active', description: 'Ready to be used in audits' },
		{ value: 'archived', label: '📦 Archived', description: 'No longer in active use' }
	];

	onMount(async () => {
		await loadFolders();
		if (checklistId) {
			isEditMode = true;
			await loadChecklist();
		}
	});

	async function loadFolders() {
		try {
			foldersLoading = true;
			// Filter folders by content_type DO (Domain) and GL (Global) as per the system convention
			const response = await fetch('/fe-api/folders/?content_type=DO&content_type=GL');
			if (response.ok) {
				const data = await response.json();
				const results = data.results || data;
				// Ensure we only map valid folders with proper IDs
				availableFolders = Array.isArray(results)
					? results
						.filter((f: any) => f && f.id && f.name)
						.map((f: any) => ({
							id: f.id,
							name: f.name
						}))
					: [];
				console.log(`Loaded ${availableFolders.length} folders:`, availableFolders);
			} else {
				console.error('Failed to load folders:', response.status, response.statusText);
				availableFolders = [];
			}
		} catch (err) {
			console.error('Error loading folders:', err);
			availableFolders = [];
		} finally {
			foldersLoading = false;
		}
	}

	async function loadChecklist() {
		try {
			loading = true;
			const checklist = await getChecklist(checklistId!);
			formData = {
				name: checklist.name,
				description: checklist.description,
				folder: checklist.folder,
				status: checklist.status,
				is_published: checklist.is_published
			};
		} catch (err) {
			console.error('Error loading checklist:', err);
			error = 'Failed to load checklist';
		} finally {
			loading = false;
		}
	}

	async function handleSubmit(event: Event) {
		event.preventDefault();

		if (!formData.name.trim()) {
			error = 'Name is required';
			return;
		}

		try {
			saving = true;
			error = '';

			// Clean the data before sending - ensure folder is null if not set
			const cleanedData = {
				...formData,
				folder: formData.folder || null
			};

			if (isEditMode) {
				await updateChecklist(checklistId!, cleanedData);
				goto(`/audits/checklists/${checklistId}`);
			} else {
				const created = await createChecklist(cleanedData);
				goto(`/audits/checklists/${created.id}`);
			}
		} catch (err) {
			console.error('Error saving checklist:', err);
			error = err instanceof Error ? err.message : 'Failed to save checklist. Please try again.';
		} finally {
			saving = false;
		}
	}

	function handleCancel() {
		if (isEditMode) {
			goto(`/audits/checklists/${checklistId}`);
		} else {
			goto('/audits/checklists');
		}
	}

	function handleChange(event: Event) {
		const target = event.target as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
		const { name, type } = target;

		let value: any;
		if (type === 'checkbox') {
			value = (target as HTMLInputElement).checked;
		} else if (name === 'folder') {
			// Convert empty string to null, otherwise keep as string (UUID)
			value = target.value && target.value !== '' && target.value !== 'null' ? target.value : null;
		} else {
			value = target.value;
		}

		formData = {
			...formData,
			[name]: value
		};
	}
</script>

<div class="p-6">
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
					{isEditMode ? 'Edit Checklist' : 'Create Checklist'}
				</h1>
				<p class="text-surface-600 dark:text-surface-400 mt-1">
					{isEditMode ? 'Update the checklist details' : 'Create a new reusable audit checklist'}
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
				<span class="text-surface-600 dark:text-surface-400 font-medium">Loading checklist...</span>
			</div>
		</div>
	{:else}
		<!-- Form -->
		<form onsubmit={handleSubmit} class="space-y-6">
			<!-- Basic Information -->
			<div class="bg-white dark:bg-surface-800 shadow-xl rounded-xl border border-surface-200 dark:border-surface-700 p-6">
				<div class="flex items-center gap-3 mb-6 pb-4 border-b border-surface-200 dark:border-surface-700">
					<div class="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
						<svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</div>
					<div>
						<h2 class="text-lg font-bold text-surface-900 dark:text-surface-50">📋 Basic Information</h2>
						<p class="text-sm text-surface-600 dark:text-surface-400">Essential details about the checklist</p>
					</div>
				</div>

				<div class="space-y-6">
					<!-- Name -->
					<div>
						<label for="name" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
							Name <span class="text-error-500">*</span>
						</label>
						<input
							id="name"
							name="name"
							type="text"
							value={formData.name}
							onchange={handleChange}
							required
							disabled={saving}
							placeholder="Enter checklist name"
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors disabled:opacity-60"
						/>
					</div>

					<!-- Description -->
					<div>
						<label for="description" class="block text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2">
							Description
						</label>
						<textarea
							id="description"
							name="description"
							value={formData.description}
							onchange={handleChange}
							disabled={saving}
							rows="4"
							placeholder="Enter checklist description..."
							class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none disabled:opacity-60"
						></textarea>
					</div>

					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<!-- Folder -->
						<div>
							<label for="folder" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
								<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
								</svg>
								Folder
							</label>
					<select
						id="folder"
						name="folder"
						value={formData.folder ?? ''}
						onchange={handleChange}
						disabled={saving || foldersLoading}
						class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors disabled:opacity-60"
					>
						{#if foldersLoading}
							<option value="">Loading folders...</option>
						{:else}
							<option value="">None (Root level)</option>
							{#each availableFolders as folder}
								<option value={folder.id}>{folder.name}</option>
							{/each}
							{#if availableFolders.length === 0}
								<option value="" disabled>No folders available</option>
							{/if}
						{/if}
						</select>
							<p class="mt-2 text-xs text-surface-500 dark:text-surface-400">
								{#if foldersLoading}
									⏳ Loading available folders...
								{:else if availableFolders.length === 0}
									ℹ️ No folders found. The checklist will be created at root level.
								{:else}
									💡 Organize checklists by domain or category ({availableFolders.length} folder{availableFolders.length === 1 ? '' : 's'} available)
								{/if}
							</p>
						</div>

						<!-- Status -->
						<div>
							<label for="status" class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-2 flex items-center gap-2">
								<svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								Status
							</label>
							<select
								id="status"
								name="status"
								onchange={handleChange}
								disabled={saving}
								class="w-full px-4 py-3 border-2 border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors disabled:opacity-60"
							>
								{#each statusChoices as choice}
									<option value={choice.value} selected={formData.status === choice.value}>
										{choice.label}
									</option>
								{/each}
							</select>
							<p class="mt-2 text-xs text-surface-500 dark:text-surface-400">
								{statusChoices.find(c => c.value === formData.status)?.description || ''}
							</p>
						</div>
					</div>

					<!-- Is Published -->
					<div class="flex items-center gap-3 p-4 bg-surface-50 dark:bg-surface-800/50 rounded-xl border-2 border-surface-200 dark:border-surface-700">
						<input
							id="is_published"
							name="is_published"
							type="checkbox"
							checked={formData.is_published}
							onchange={handleChange}
							disabled={saving}
							class="h-4 w-4 text-primary-600 focus:ring-2 focus:ring-primary-500 border-surface-300 dark:border-surface-600 rounded disabled:opacity-60"
						/>
						<label for="is_published" class="text-sm font-semibold text-surface-900 dark:text-surface-50 cursor-pointer select-none flex items-center gap-2">
							<svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
							</svg>
							Published
						</label>
						<span class="text-xs text-surface-600 dark:text-surface-400 ml-auto">Visible to other users</span>
					</div>
				</div>
			</div>

			<!-- Info Box -->
			{#if isEditMode}
				<div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 flex items-start gap-3">
					<svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<div class="text-sm text-blue-800 dark:text-blue-200">
						<strong>Note:</strong> To manage checklist items (add, edit, delete), please save the checklist and use the detail view.
					</div>
				</div>
			{:else}
				<div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-4 flex items-start gap-3">
					<svg class="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<div class="text-sm text-green-800 dark:text-green-200">
						<strong>Next Step:</strong> After creating the checklist, you can add test items that link to controls, risks, and policies.
					</div>
				</div>
			{/if}

			<!-- Actions -->
			<div class="sticky bottom-0 bg-gradient-to-r from-surface-50 to-surface-100 dark:from-surface-900 dark:to-surface-800 border-t-2 border-surface-200 dark:border-surface-700 p-6 rounded-xl shadow-xl">
				<div class="flex justify-end gap-3">
					<button
						type="button"
						onclick={handleCancel}
						disabled={saving}
						class="px-6 py-3 border-2 border-surface-300 dark:border-surface-600 rounded-xl shadow-sm text-sm font-semibold text-surface-700 dark:text-surface-200 bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
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
							{isEditMode ? 'Updating...' : 'Creating...'}
						{:else}
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
							</svg>
							{isEditMode ? 'Update Checklist' : 'Create Checklist'}
						{/if}
					</button>
				</div>
			</div>
		</form>
	{/if}
</div>
