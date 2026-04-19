<script lang="ts">
	import { onMount } from 'svelte';
	import HierarchyTree from './HierarchyTree.svelte';
	import { uploadHierarchyCSV } from './api.js';

	export let refreshTrigger = 0;
	export let activeTab: string = 'all'; // Filter tab from parent: 'all', 'my_entities', 'my_team'

	let localTab = 'tree'; // Local tab: 'tree' or 'upload'
	let csvFile: File | null = null;
	let uploading = false;
	let uploadError: string | null = null;
	let uploadSuccess: string | null = null;
	let csvTemplate = `entity_name,parent_name,type
Finance Department,,business_unit
Financial Reporting Process,Finance Department,process
ERP Financial Module,Financial Reporting Process,system
HR Department,,business_unit
Payroll Process,HR Department,process
HRIS System,Payroll Process,system
IT Department,,business_unit
Infrastructure Division,IT Department,division
Network Operations,Infrastructure Division,function
Database Administration,Infrastructure Division,function
Security Operations,IT Department,function
SOC Team,Security Operations,unit
Incident Response,Security Operations,unit`;

	function handleTabChange(tab: string) {
		localTab = tab;
		uploadError = null;
		uploadSuccess = null;
	}

	function handleFileSelect(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		csvFile = (input.files && input.files[0]) || null;
		uploadError = null;
		uploadSuccess = null;
	}

	async function uploadCSV() {
		if (!csvFile) return;
		
		try {
			uploading = true;
			uploadError = null;
			uploadSuccess = null;
			
			const result = await uploadHierarchyCSV(csvFile);
			
			uploadSuccess = result.message;
			if (result.errors && result.errors.length > 0) {
				uploadError = `Errors: ${result.errors.join(', ')}`;
			}
			
			// Refresh the hierarchy
			refreshTrigger += 1;
			
		} catch (err: any) {
			uploadError = err.message;
		} finally {
			uploading = false;
		}
	}

	function downloadTemplate() {
		const blob = new Blob([csvTemplate], { type: 'text/csv' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'organizational_structure_template.csv';
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
	}
</script>

<div class="bg-surface-50 shadow overflow-hidden sm:rounded-md">
	<!-- Tab Navigation -->
	<div class="bg-surface-100 px-6 py-4 border-b border-surface-200">
		<div class="flex space-x-8">
			<button
				onclick={() => handleTabChange('tree')}
				class="py-2 px-1 border-b-2 font-medium text-sm {localTab === 'tree' ? 'border-primary-500 text-primary-600' : 'border-transparent text-surface-500 hover:text-surface-700 hover:border-surface-300'}"
			>
				<svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
				</svg>
				Tree View
			</button>
			<button
				onclick={() => handleTabChange('upload')}
				class="py-2 px-1 border-b-2 font-medium text-sm {localTab === 'upload' ? 'border-primary-500 text-primary-600' : 'border-transparent text-surface-500 hover:text-surface-700 hover:border-surface-300'}"
			>
				<svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
				</svg>
				CSV Upload
			</button>
		</div>
	</div>

	<!-- Tab Content -->
	<div class="p-6">
		{#if localTab === 'tree'}
			<div class="space-y-4">
				<div class="flex items-center justify-between">
					<div>
						<h3 class="text-lg font-medium text-surface-900">Organizational Structure</h3>
						<p class="text-sm text-surface-500">Hierarchical view of audit entities based on parent-child relationships</p>
					</div>
					<button
						onclick={() => refreshTrigger += 1}
						class="px-3 py-2 text-sm text-surface-600 border border-surface-300 rounded-md hover:bg-surface-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
					>
						<svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
						</svg>
						Refresh
					</button>
				</div>
				
				<HierarchyTree {refreshTrigger} filterTab={activeTab} />
			</div>
		{:else if localTab === 'upload'}
			<div class="space-y-6">
				<div>
					<h3 class="text-lg font-medium text-surface-900">Upload Organizational Structure</h3>
					<p class="text-sm text-surface-500">Upload a CSV file to create or update the organizational hierarchy</p>
				</div>

				<!-- CSV Template -->
				<div class="bg-blue-50 border border-blue-200 rounded-md p-4">
					<div class="flex items-start">
						<svg class="w-5 h-5 text-blue-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<div class="flex-1">
							<h4 class="text-sm font-medium text-blue-800">CSV Format</h4>
							<p class="text-sm text-blue-700 mt-1">
								Your CSV should have columns: <code class="bg-blue-100 px-1 rounded">entity_name</code>, 
								<code class="bg-blue-100 px-1 rounded">parent_name</code>, 
								<code class="bg-blue-100 px-1 rounded">type</code>
							</p>
							<p class="text-sm text-blue-700 mt-1">
								Leave <code class="bg-blue-100 px-1 rounded">parent_name</code> empty for top-level entities.
							</p>
							<button
								onclick={downloadTemplate}
								class="mt-2 text-sm text-blue-600 hover:text-blue-800 underline"
							>
								Download template CSV
							</button>
						</div>
					</div>
				</div>

				<!-- Upload Form -->
				<div class="space-y-4">
					<div>
						<label for="csv-file" class="block text-sm font-medium text-surface-700 mb-2">
							Select CSV File
						</label>
						<input
							id="csv-file"
							type="file"
							accept=".csv"
							onchange={handleFileSelect}
							class="block w-full text-sm text-surface-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
						/>
					</div>

					{#if csvFile}
						<div class="flex items-center space-x-2 text-sm text-surface-600">
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							<span>Selected: {csvFile.name}</span>
						</div>
					{/if}

					<button
						onclick={uploadCSV}
						disabled={!csvFile || uploading}
						class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{uploading ? 'Uploading...' : 'Upload CSV'}
					</button>
				</div>

				<!-- Upload Results -->
				{#if uploadSuccess}
					<div class="bg-green-50 border border-green-200 rounded-md p-4">
						<div class="flex">
							<svg class="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							<div>
								<h4 class="text-sm font-medium text-green-800">Upload Successful</h4>
								<p class="text-sm text-green-700 mt-1">{uploadSuccess}</p>
							</div>
						</div>
					</div>
				{/if}

				{#if uploadError}
					<div class="bg-red-50 border border-red-200 rounded-md p-4">
						<div class="flex">
							<svg class="w-5 h-5 text-red-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							<div>
								<h4 class="text-sm font-medium text-red-800">Upload Error</h4>
								<p class="text-sm text-red-700 mt-1">{uploadError}</p>
							</div>
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>
