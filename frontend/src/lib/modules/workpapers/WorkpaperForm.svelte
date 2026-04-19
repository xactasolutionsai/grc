<script lang="ts">
	import { onMount } from 'svelte';
	import { createWorkpaper, uploadFile } from './api.js';
	import FormSection from './FormSection.svelte';

	export let onSaved = () => {};
	export let workpaper: any = null; // For editing existing workpaper

	let form = {
		title: '',
		description: '',
		workpaper_type: 'other',
		external_link: '',
		tags: null as string[] | null,
		metadata: null as any,
		notes: '',
		is_active: true
	};

	let saving = false;
	let uploading = false;
	let error: string | null = null;
	let selectedFile: File | null = null;
	let tagsInput = '';
	let uploadProgress = '';

	const workpaperTypes = [
		{ value: 'excel', label: '📊 Excel Spreadsheet', icon: '📊' },
		{ value: 'word', label: '📄 Word Document', icon: '📄' },
		{ value: 'pdf', label: '📋 PDF Document', icon: '📋' },
		{ value: 'image', label: '🖼️ Image', icon: '🖼️' },
		{ value: 'link', label: '🔗 External Link', icon: '🔗' },
		{ value: 'other', label: '📎 Other', icon: '📎' }
	];

	onMount(() => {
		// If editing, populate form
		if (workpaper) {
			form = {
				title: workpaper.title || '',
				description: workpaper.description || '',
				workpaper_type: workpaper.workpaper_type || 'other',
				external_link: workpaper.external_link || '',
				tags: workpaper.tags || null,
				metadata: workpaper.metadata || null,
				notes: workpaper.notes || '',
				is_active: workpaper.is_active !== undefined ? workpaper.is_active : true
			};
			
			if (workpaper.tags && Array.isArray(workpaper.tags)) {
				tagsInput = workpaper.tags.join(', ');
			}
		}
	});

	function handleChange(event: any) {
		const { name, value, type, checked } = event.target;
		form = {
			...form,
			[name]: type === 'checkbox' ? checked : value
		};
	}

	function handleFileSelect(event: any) {
		const input = event.target as HTMLInputElement;
		if (input.files && input.files[0]) {
			selectedFile = input.files[0];
		}
	}

	function handleTagsChange(event: any) {
		tagsInput = event.target.value;
		// Parse tags (comma or space separated)
		if (tagsInput.trim()) {
			form.tags = tagsInput.split(/[,\s]+/).filter(tag => tag.trim() !== '').map(tag => tag.trim());
		} else {
			form.tags = null;
		}
	}

	async function handleSubmit(event: any) {
		event.preventDefault();
		saving = true;
		uploading = false;
		error = null;
		uploadProgress = '';

		try {
			// Validate required fields
			if (!form.title || !form.title.trim()) {
				throw new Error('Title is required');
			}

			// For link type, ensure external_link is provided
			if (form.workpaper_type === 'link' && !form.external_link) {
				throw new Error('External link is required for link type workpapers');
			}

			// Clean up form data
			const formData: any = { ...form };
			
			// Remove empty optional fields
			if (!formData.description || formData.description.trim() === '') formData.description = '';
			if (!formData.external_link || formData.external_link.trim() === '') delete formData.external_link;
			if (!formData.tags || formData.tags.length === 0) delete formData.tags;
			if (!formData.metadata) delete formData.metadata;
			
			uploadProgress = 'Creating workpaper...';
			const created: any = await createWorkpaper(formData);
			
			// If there's a file, upload it
			if (selectedFile && created && created.id) {
				uploading = true;
				uploadProgress = 'Uploading file...';
				
				try {
					await uploadFile(created.id, selectedFile);
					uploadProgress = 'File uploaded successfully!';
					uploading = false;
				} catch (uploadErr: any) {
					uploading = false;
					error = `Workpaper created, but file upload failed: ${uploadErr.message || 'Unknown error'}`;
					saving = false;
					return; // Don't close modal, keep it open to show error
				}
			}
			
			uploadProgress = 'Complete!';
			
			// Small delay to show success message
			await new Promise(resolve => setTimeout(resolve, 500));
			
			onSaved();
			
			// Reset form
			form = {
				title: '',
				description: '',
				workpaper_type: 'other',
				external_link: '',
				tags: null,
				metadata: null,
				notes: '',
				is_active: true
			};
			selectedFile = null;
			tagsInput = '';
			uploadProgress = '';
		} catch (err: any) {
			console.error('Error creating workpaper:', err);
			error = err.message || 'An error occurred while creating the workpaper';
		} finally {
			saving = false;
			uploading = false;
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

	{#if uploadProgress}
		<div class="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg p-4 mb-4 flex items-start gap-3">
			<svg class="h-5 w-5 text-primary-600 dark:text-primary-400 mt-0.5 {uploading || saving ? 'animate-spin' : ''}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
			</svg>
			<div class="text-primary-800 dark:text-primary-200 text-sm">{uploadProgress}</div>
		</div>
	{/if}

	<form on:submit={handleSubmit} class="space-y-4">
		<!-- Basic Information Section -->
		<FormSection title="Basic Information" subtitle="Required fields">
			<div class="space-y-4">
				<div>
					<label for="title" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Title <span class="text-error-500">*</span>
					</label>
					<input
						id="title"
						name="title"
						type="text"
						bind:value={form.title}
						on:change={handleChange}
						required
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
						placeholder="Enter workpaper title"
					/>
				</div>

				<div>
					<label for="workpaper_type" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Type <span class="text-error-500">*</span>
					</label>
					<select
						id="workpaper_type"
						name="workpaper_type"
						bind:value={form.workpaper_type}
						on:change={handleChange}
						required
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
					>
						{#each workpaperTypes as type}
							<option value={type.value}>{type.label}</option>
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
						placeholder="Enter detailed description of the workpaper"
					></textarea>
				</div>
			</div>
		</FormSection>

		<!-- File Upload / External Link Section -->
		<FormSection title="File or Link" subtitle="Upload a file or provide an external link">
			<div class="space-y-4">
				{#if form.workpaper_type === 'link'}
					<!-- External Link Input -->
					<div>
						<label for="external_link" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							External Link <span class="text-error-500">*</span>
						</label>
						<div class="relative">
							<svg class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
							</svg>
							<input
								id="external_link"
								name="external_link"
								type="url"
								bind:value={form.external_link}
								on:change={handleChange}
								required={form.workpaper_type === 'link'}
								class="w-full pl-10 pr-4 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
								placeholder="https://example.com/document"
							/>
						</div>
						<p class="text-xs text-surface-500 dark:text-surface-400 mt-1">🔗 Provide a full URL to an external document or resource.</p>
					</div>
				{:else}
					<!-- File Upload Input -->
					<div>
						<label for="file" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
							Upload File
						</label>
						<div class="relative">
							<input
								id="file"
								type="file"
								on:change={handleFileSelect}
								accept=".xlsx,.xls,.doc,.docx,.pdf,.jpg,.jpeg,.png,.gif,.txt,.csv"
								class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 dark:file:bg-primary-900/20 file:text-primary-700 dark:file:text-primary-300 hover:file:bg-primary-100 dark:hover:file:bg-primary-900/30"
							/>
						</div>
						<p class="text-xs text-surface-500 dark:text-surface-400 mt-1">
							📎 Accepted formats: Excel, Word, PDF, images, text files (max 25MB).
						</p>
						{#if selectedFile}
							<div class="mt-2 flex items-center gap-2 p-2 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
								<svg class="h-4 w-4 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<span class="text-sm text-primary-700 dark:text-primary-300">{selectedFile.name}</span>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		</FormSection>

		<!-- Metadata Section -->
		<FormSection title="Metadata" subtitle="Tags and categorization" collapsible={true} defaultOpen={false}>
			<div class="space-y-4">
				<div>
					<label for="tags" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
						Tags
					</label>
					<input
						id="tags"
						type="text"
						bind:value={tagsInput}
						on:input={handleTagsChange}
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
						placeholder="Enter tags separated by commas (e.g., audit, compliance, Q1-2024)"
					/>
					<p class="text-xs text-surface-500 dark:text-surface-400 mt-1">🏷️ Use tags to categorize and search workpapers easily.</p>
					{#if form.tags && form.tags.length > 0}
						<div class="mt-2 flex flex-wrap gap-2">
							{#each form.tags as tag}
								<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-200">
									{tag}
								</span>
							{/each}
						</div>
					{/if}
				</div>
			</div>
		</FormSection>

		<!-- Additional Information Section -->
		<FormSection title="Additional Information" subtitle="Notes" collapsible={true} defaultOpen={false}>
			<div class="space-y-4">
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
						class="w-full px-3 py-2 border border-surface-300 dark:border-surface-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-surface-900 text-surface-900 dark:text-surface-50"
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
						Active Workpaper
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
				disabled={saving || uploading}
				class="px-5 py-2.5 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
			>
				{#if saving || uploading}
					<svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					{#if uploading}
						Uploading file...
					{:else}
						Creating...
					{/if}
				{:else}
					<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
					</svg>
					Create Workpaper
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

