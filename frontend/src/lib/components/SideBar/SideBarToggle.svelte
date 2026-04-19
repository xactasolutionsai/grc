<script lang="ts">
    interface Props {
        open: boolean;
    }

    let { open = $bindable() }: Props = $props();

    function toggle() {
        open = !open;
    }

    let classesSidebarOpenButton = $derived((open: boolean) =>
        open ? 'left-[15.3rem]' : 'rotate-180 left-5'
    );
</script>

<!-- SIDEBAR TOGGLE -->
<button
        onclick={toggle}
        class="{classesSidebarOpenButton(
		open
	)} z-20 fixed w-8 h-8 rounded-full content-center self-center bg-white shadow-lg border-2 border-primary-300 text-primary-700 hover:scale-110 hover:shadow-xl hover:bg-primary-600 hover:text-white hover:border-primary-600 transition-all duration-300 top-1/2 bottom-1/2"
        data-testid="sidebar-toggle-btn"
>
    <i class="fa-solid fa-angle-left"></i>
</button>
