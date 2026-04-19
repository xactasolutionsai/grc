<script lang="ts">
    import { page } from '$app/state';
    import { safeTranslate } from '$lib/utils/i18n';
    import Anchor from '$lib/components/Anchor/Anchor.svelte';

    interface Props {
        item?: { name: string; href: string; fa_icon: string }[];
        sideBarVisibleItems: Record<string, boolean>;
    }

    let { item = [], sideBarVisibleItems }: Props = $props();

    let classesActive = $derived((href: string) =>
        href === page.url.pathname
            ? 'bg-gradient-to-r from-primary-100 via-secondary-50 to-tertiary-50 text-primary-800 font-semibold border-l-4 border-secondary-500 shadow-md'
            : 'text-surface-700 hover:text-secondary-700 hover:bg-gradient-to-r hover:from-secondary-50 hover:to-tertiary-50 border-l-4 border-transparent hover:border-secondary-400'
    );
</script>

{#each item as item}
    <!-- undefined and true must be shown -->
    {#if sideBarVisibleItems[item.name] !== false}
        <Anchor
                href={item.href}
                breadcrumbAction="replace"
                class="unstyled flex whitespace-nowrap items-center py-3 px-3 text-sm font-normal rounded-lg transition-all duration-200 {classesActive(
				item.href ?? ''
			)}"
                data-testid={'accordion-item-' + item.href.substring(1)}
        >
			<span
                    class="flex items-center w-full space-x-3"
                    id={item.name}
                    title={safeTranslate(item.name)}
            >
				<i class="{item.fa_icon} w-5 text-center"></i>
				<span class="text-sm tracking-wide truncate font-medium">{safeTranslate(item.name)}</span>
			</span>
        </Anchor>
    {/if}
{/each}
