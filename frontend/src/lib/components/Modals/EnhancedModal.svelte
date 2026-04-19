<script lang="ts">
	import { fly, fade } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';

	interface Props {
		/** Whether the modal is visible */
		open?: boolean;
		/** Modal title */
		title?: string;
		/** Maximum width of the modal */
		maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | 'full';
		/** Whether to show the close button */
		showCloseButton?: boolean;
		/** Whether clicking the backdrop closes the modal */
		closeOnBackdrop?: boolean;
		/** Whether pressing Escape closes the modal */
		closeOnEscape?: boolean;
		/** Custom modal classes */
		modalClass?: string;
		/** Custom backdrop classes */
		backdropClass?: string;
		/** Whether to show header */
		showHeader?: boolean;
		/** Whether to show footer */
		showFooter?: boolean;
		/** Footer alignment */
		footerAlign?: 'left' | 'center' | 'right';
		/** z-index for the modal */
		zIndex?: string;
		/** onClose callback */
		onClose?: () => void;
		/** children */
		children?: any;
	}

	let {
		open = $bindable(false),
		title = '',
		maxWidth = '3xl',
		showCloseButton = true,
		closeOnBackdrop = true,
		closeOnEscape = true,
		modalClass = '',
		backdropClass = '',
		showHeader = true,
		showFooter = false,
		footerAlign = 'right',
		zIndex = 'z-50',
		onClose,
		children
	}: Props = $props();

	// Map maxWidth to Tailwind classes
	const maxWidthClasses: Record<string, string> = {
		sm: 'sm:max-w-sm',
		md: 'sm:max-w-md',
		lg: 'sm:max-w-lg',
		xl: 'sm:max-w-xl',
		'2xl': 'sm:max-w-2xl',
		'3xl': 'sm:max-w-3xl',
		'4xl': 'sm:max-w-4xl',
		'5xl': 'sm:max-w-5xl',
		full: 'sm:max-w-full'
	};

	// Footer alignment classes
	const footerAlignClasses: Record<string, string> = {
		left: 'justify-start',
		center: 'justify-center',
		right: 'justify-end'
	};

	function handleClose() {
		open = false;
		if (onClose) onClose();
	}

	function handleBackdropClick(event: MouseEvent) {
		if (closeOnBackdrop && event.target === event.currentTarget) {
			handleClose();
		}
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (closeOnEscape && event.key === 'Escape') {
			handleClose();
		}
	}
</script>

{#if open}
	<!-- Modal Container -->
	<div
		class="fixed inset-0 {zIndex} overflow-y-auto"
		on:click={handleBackdropClick}
		on:keydown={handleKeyDown}
		role="dialog"
		aria-modal="true"
		aria-labelledby={title ? 'enhanced-modal-title' : undefined}
		tabindex="-1"
		transition:fade={{ duration: 200 }}
	>
		<!-- Backdrop -->
		<div
			class="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity {backdropClass}"
			transition:fade={{ duration: 200 }}
		></div>

		<!-- Modal Content Container -->
		<div class="flex min-h-full items-center justify-center p-4 text-center sm:p-6">
			<div
				class="relative transform overflow-hidden rounded-xl bg-surface-50 dark:bg-surface-900 text-left shadow-2xl transition-all w-full {maxWidthClasses[
					maxWidth
				]} {modalClass}"
				transition:fly={{ y: 20, duration: 300, easing: quintOut }}
			>
				<!-- Close Button -->
				{#if showCloseButton}
					<button
						type="button"
						on:click={handleClose}
						class="absolute top-4 right-4 text-surface-400 hover:text-surface-600 dark:hover:text-surface-200 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-full p-1.5 transition-colors duration-200 hover:bg-surface-100 dark:hover:bg-surface-800 z-10"
						aria-label="Close modal"
					>
						<svg
							class="h-5 w-5"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							stroke-width="2"
						>
							<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				{/if}

				<!-- Header -->
				{#if showHeader && title}
					<div class="border-b border-surface-200 dark:border-surface-700 px-6 py-5 pr-14">
						<h2
							id="enhanced-modal-title"
							class="text-2xl font-bold text-surface-900 dark:text-surface-50"
						>
							{title}
						</h2>
					</div>
				{/if}

				<!-- Body -->
				<div class="px-6 py-6">
					{@render children?.()}
				</div>

				<!-- Footer -->
				{#if showFooter}
					<div
						class="border-t border-surface-200 dark:border-surface-700 px-6 py-4 flex gap-3 {footerAlignClasses[
							footerAlign
						]}"
					>
						{#if children?.footer}
							{@render children.footer()}
						{/if}
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
	/* Smooth scroll for modal content */
	:global(.enhanced-modal-body) {
		max-height: calc(100vh - 200px);
		overflow-y: auto;
	}

	/* Custom scrollbar styling */
	:global(.enhanced-modal-body)::-webkit-scrollbar {
		width: 8px;
	}

	:global(.enhanced-modal-body)::-webkit-scrollbar-track {
		background: transparent;
	}

	:global(.enhanced-modal-body)::-webkit-scrollbar-thumb {
		background: rgba(0, 0, 0, 0.2);
		border-radius: 4px;
	}

	:global(.enhanced-modal-body)::-webkit-scrollbar-thumb:hover {
		background: rgba(0, 0, 0, 0.3);
	}
</style>
