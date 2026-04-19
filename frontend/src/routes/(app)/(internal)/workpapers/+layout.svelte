<script lang="ts">
	import type { PageData } from './$types';

	interface Props {
		data: PageData;
		children?: any;
	}

	let { data, children }: Props = $props();
</script>

{@render children?.()}

