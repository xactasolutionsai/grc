<script lang="ts">
    import { safeTranslate } from '$lib/utils/i18n';
    interface Props {
        item: any; // Specify the type of 'item' as a key of 'Sidebar'
    }

    let { item }: Props = $props();
</script>

<span
        class="whitespace-nowrap text-surface-700 font-bold uppercase tracking-wider text-xs flex items-center gap-2 hover:text-secondary-600 transition-colors"
        data-testid={'accordion-item-' + item.name.toLowerCase().replace(' ', '-')}
>
	<span class="w-1.5 h-1.5 bg-gradient-to-r from-secondary-500 via-tertiary-400 to-primary-500 rounded-full shadow-sm"></span>
    {safeTranslate(item.name)}
</span>
