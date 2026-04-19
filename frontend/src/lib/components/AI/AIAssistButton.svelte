<script lang="ts">
	import { Sparkles } from 'lucide-svelte';

	interface Props {
		onclick: () => void | Promise<void>;
		loading?: boolean;
		disabled?: boolean;
		label: string;
		title?: string;
		variant?: 'primary' | 'subtle' | 'ghost';
		size?: 'sm' | 'md';
		type?: 'button' | 'submit';
		fullWidth?: boolean;
	}

	let {
		onclick,
		loading = false,
		disabled = false,
		label,
		title,
		variant = 'subtle',
		size = 'md',
		type = 'button',
		fullWidth = false
	}: Props = $props();

	const variantClass = $derived(
		variant === 'primary'
			? 'preset-filled-primary-500'
			: variant === 'ghost'
				? 'preset-tonal'
				: 'preset-filled-secondary-500'
	);
	const sizeClass = $derived(size === 'sm' ? 'btn-sm text-xs' : '');
</script>

<button
	{type}
	class="btn {variantClass} {sizeClass} {fullWidth ? 'w-full' : ''} font-semibold"
	{title}
	disabled={disabled || loading}
	onclick={(e) => {
		e.preventDefault();
		onclick();
	}}
	data-testid="ai-assist-button"
>
	{#if loading}
		<svg
			class="animate-spin h-4 w-4 mr-1"
			xmlns="http://www.w3.org/2000/svg"
			fill="none"
			viewBox="0 0 24 24"
			aria-hidden="true"
		>
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
			></circle>
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
			></path>
		</svg>
	{:else}
		<Sparkles class="h-4 w-4 mr-1" aria-hidden="true" />
	{/if}
	<span>{label}</span>
</button>
