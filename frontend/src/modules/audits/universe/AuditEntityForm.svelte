<script>
	import { createEntity } from './api.js';

	export let onSaved = () => {};

	let form = {
		name: '',
		entity_type: 'process',
		description: '',
		risk_score: 0,
		owner: null,
		regulatory_relevance: null,
		last_audited: '',
		is_active: true
	};
	
	let saving = false;
	let error = null;

	const entityTypes = [
		{ value: 'business_unit', label: 'Business Unit' },
		{ value: 'process', label: 'Process' },
		{ value: 'system', label: 'System' },
		{ value: 'vendor', label: 'Vendor' },
		{ value: 'compliance_domain', label: 'Compliance Domain' }
	];

	function handleChange(event) {
		const { name, value, type, checked } = event.target;
		form = {
			...form,
			[name]: type === 'checkbox' ? checked : value
		};
	}

	async function handleSubmit(event) {
		event.preventDefault();
		saving = true;
		error = null;
		
		try {
			// Clean up form data
			const formData = { ...form };
			if (!formData.last_audited) delete formData.last_audited;
			if (!formData.owner) delete formData.owner;
			if (!formData.regulatory_relevance) delete formData.regulatory_relevance;
			
			await createEntity(formData);
			onSaved();
			
			// Reset form
			form = {
				name: '',
				entity_type: 'process',
				description: '',
				risk_score: 0,
				owner: null,
				regulatory_relevance: null,
				last_audited: '',
				is_active: true
			};
		} catch (err) {
			console.error('Error creating entity:', err);
			error = err.message;
		} finally {
			saving = false;
		}
	}
</script>

<div class="max-w-2xl mx-auto p-6">
	<h2 class="text-2xl font-bold text-gray-900 mb-6">Create Audit Entity</h2>
	
	{#if error}
		<div class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
			<div class="text-red-800">Error: {error}</div>
		</div>
	{/if}

	<form on:submit={handleSubmit} class="space-y-6">
		<div>
			<label for="name" class="block text-sm font-medium text-gray-700 mb-2">
				Name *
			</label>
			<input
				id="name"
				name="name"
				type="text"
				bind:value={form.name}
				on:change={handleChange}
				required
				class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
				placeholder="Enter entity name"
			/>
		</div>

		<div>
			<label for="entity_type" class="block text-sm font-medium text-gray-700 mb-2">
				Type *
			</label>
			<select
				id="entity_type"
				name="entity_type"
				bind:value={form.entity_type}
				on:change={handleChange}
				class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
			>
				{#each entityTypes as type}
					<option value={type.value}>{type.label}</option>
				{/each}
			</select>
		</div>

		<div>
			<label for="description" class="block text-sm font-medium text-gray-700 mb-2">
				Description
			</label>
			<textarea
				id="description"
				name="description"
				bind:value={form.description}
				on:change={handleChange}
				rows="3"
				class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
				placeholder="Enter entity description"
			></textarea>
		</div>

		<div>
			<label for="risk_score" class="block text-sm font-medium text-gray-700 mb-2">
				Risk Score
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
				class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
			/>
		</div>

		<div>
			<label for="last_audited" class="block text-sm font-medium text-gray-700 mb-2">
				Last Audited
			</label>
			<input
				id="last_audited"
				name="last_audited"
				type="date"
				bind:value={form.last_audited}
				on:change={handleChange}
				class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
			/>
		</div>

		<div class="flex items-center">
			<input
				id="is_active"
				name="is_active"
				type="checkbox"
				bind:checked={form.is_active}
				on:change={handleChange}
				class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
			/>
			<label for="is_active" class="ml-2 block text-sm text-gray-900">
				Active
			</label>
		</div>

		<div class="flex justify-end space-x-3">
			<button
				type="button"
				on:click={() => onSaved()}
				class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
			>
				Cancel
			</button>
			<button
				type="submit"
				disabled={saving}
				class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
			>
				{saving ? 'Creating...' : 'Create Entity'}
			</button>
		</div>
	</form>
</div>
