<script lang="ts">
    import { run } from 'svelte/legacy';

    // Most of your app wide CSS should be put in this file
    import '../../app.css';

    import { AppBar } from '@skeletonlabs/skeleton-svelte';
    import { safeTranslate } from '$lib/utils/i18n';

    import SideBar from '$lib/components/SideBar/SideBar.svelte';
    import Breadcrumbs from '$lib/components/Breadcrumbs/Breadcrumbs.svelte';
    import { pageTitle, clientSideToast } from '$lib/utils/stores';
    import { getCookie, deleteCookie } from '$lib/utils/cookies';
    import { browser } from '$app/environment';
    import { m } from '$paraglide/messages';

    import type { PageData, ActionData } from './$types';
    import QuickStartModal from '$lib/components/SideBar/QuickStart/QuickStartModal.svelte';

    import { getSidebarVisibleItems } from '$lib/utils/sidebar-config';
    import {
        getModalStore,
        type ModalComponent,
        type ModalSettings,
        type ModalStore
    } from '$lib/components/Modals/stores';

    import CommandPalette from '$lib/components/CommandPalette/CommandPalette.svelte';
    import { interceptExternalLinks, setGlobalModalStore } from '$lib/utils/external-links';

    let sidebarOpen = $state(true);

    let classesSidebarOpen = $derived((open: boolean) => (open ? 'ml-64' : 'ml-7'));

    interface Props {
        data: PageData;
        form: ActionData;
        sideBarVisibleItems?: any;
        children?: import('svelte').Snippet;
    }

    let {
        data,
        form,
        sideBarVisibleItems = getSidebarVisibleItems(data?.featureflags),
        children
    }: Props = $props();

    const modalStore: ModalStore = getModalStore();

    // Initialize external link interceptor
    $effect(() => {
        if (browser) {
            setGlobalModalStore(modalStore);
            interceptExternalLinks();
        }
    });

    // Handle login-specific logic
    run(() => {
        if (browser) {
            const fromLogin = getCookie('from_login');
            if (fromLogin === 'true') {
                deleteCookie('from_login');
                fetch('/fe-api/waiting-risk-acceptances').then(async (res) => {
                    const data = await res.json();
                    const number = data.count ?? 0;
                    if (number <= 0) return;
                    // clientSideToast.set({
                    // 	message: m.waitingRiskAcceptances({
                    // 		number: number,
                    // 		s: number > 1 ? 's' : '',
                    // 		itPlural: number > 1 ? 'i' : 'e'
                    // 	}),
                    // 	type: 'info'
                    // });
                });
            }
        }
    });

    function modalQuickStart(): void {
        let modalComponent: ModalComponent = {
            ref: QuickStartModal,
            props: {}
        };
        let modal: ModalSettings = {
            type: 'component',
            component: modalComponent,
            // Data
            title: m.quickStart()
        };
        modalStore.trigger(modal);
    }
</script>

<!-- App Shell -->
<div class="overflow-x-hidden">
    <SideBar bind:open={sidebarOpen} {sideBarVisibleItems} />
    <AppBar
            base="relative transition-all duration-300 {classesSidebarOpen(sidebarOpen)}"
            background="bg-gradient-to-r from-primary-700 via-secondary-500 to-tertiary-600 shadow-lg"
            padding="pb-3 px-6"
    >
        {#snippet headline()}
			<span
                    class="text-3xl font-bold pb-1 text-white drop-shadow-sm"
                    id="page-title"
            >
				{safeTranslate($pageTitle)}
			</span>
            {#if data?.user?.is_admin}
                <button
                        onclick={modalQuickStart}
                        class="absolute top-6 right-9 px-5 py-2.5 rounded-xl bg-white text-primary-700 text-sm font-bold shadow-lg
        ring-2 ring-white/50 ring-offset-2 ring-offset-primary-600 transition-all duration-300 hover:bg-secondary-400 hover:text-white
        hover:ring-secondary-300 hover:shadow-2xl hover:scale-110
        focus:outline-hidden active:scale-95"
                >
                    <i class="fa-solid fa-sparkles mr-2"></i>{m.quickStart()}
                </button>
            {/if}
            <hr class="w-screen my-2 border-t-2 border-white/30" />
            <Breadcrumbs />
        {/snippet}
    </AppBar>
    <!-- Router Slot -->
    <CommandPalette />
    <main
            class="min-h-screen p-8 bg-gradient-to-br from-surface-50 via-primary-50/30 to-secondary-50/30 transition-all duration-300 {classesSidebarOpen(
			sidebarOpen
		)}"
    >
        {@render children?.()}
    </main>
    <!-- ---- / ---- -->
</div>
