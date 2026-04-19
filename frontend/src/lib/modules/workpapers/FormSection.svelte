<script lang="ts">
	interface Props {
		title: string;
		subtitle?: string;
		badge?: string;
		collapsible?: boolean;
		defaultOpen?: boolean;
		children?: any;
	}

	let {
		title,
		subtitle = '',
		badge = '',
		collapsible = false,
		defaultOpen = true,
		children
	}: Props = $props();

	let isOpen = $state(defaultOpen);

	function toggleSection() {
		if (collapsible) {
			isOpen = !isOpen;
		}
	}
</script>

<div class="form-section border border-surface-200 dark:border-surface-700 rounded-lg overflow-hidden bg-white dark:bg-surface-800 mb-4">
	<!-- Section Header -->
	<button
		type="button"
		class="w-full px-5 py-4 flex items-center justify-between bg-surface-50 dark:bg-surface-800 border-b border-surface-200 dark:border-surface-700 {collapsible
			? 'cursor-pointer hover:bg-surface-100 dark:hover:bg-surface-700'
			: 'cursor-default'}"
		onclick={toggleSection}
		disabled={!collapsible}
	>
		<div class="flex items-center gap-3">
			<h3 class="text-base font-semibold text-surface-900 dark:text-surface-50">
				{title}
			</h3>
			{#if badge}
				<span
					class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100"
				>
					{badge}
				</span>
			{/if}
		</div>
		<div class="flex items-center gap-3">
			{#if subtitle}
				<span class="text-sm text-surface-500 dark:text-surface-400 hidden sm:block">
					{subtitle}
				</span>
			{/if}
			{#if collapsible}
				<svg
					class="h-5 w-5 text-surface-400 transition-transform duration-200 {isOpen
						? 'rotate-180'
						: ''}"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
				</svg>
			{/if}
		</div>
	</button>

	<!-- Section Content -->
	{#if isOpen}
		<div class="p-5">
			{@render children?.()}
		</div>
	{/if}
</div>

<style>
	.form-section {
		transition: all 0.2s ease-in-out;
	}
</style>

