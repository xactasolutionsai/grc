<script lang="ts">
    import { page } from '$app/state';
    import { LOCALE_MAP, language, defaultLangLabels } from '$lib/utils/locales';
    import { m } from '$paraglide/messages';
    import { getLocale, locales, setLocale } from '$paraglide/runtime';
    import { Popover } from '@skeletonlabs/skeleton-svelte';

    import { getModalStore, type ModalSettings } from '$lib/components/Modals/stores';
    import { createEventDispatcher, onMount } from 'svelte';
    const dispatch = createEventDispatcher();

    const modalStore = getModalStore();

    let value = $state(getLocale());
    async function handleLocaleChange(event: Event) {
        value = event?.target?.value;
        await fetch('/fe-api/user-preferences', {
            method: 'PATCH',
            body: JSON.stringify({
                lang: value
            })
        }).then(() => setLocale(value));
    }

    async function modalBuildInfo() {
        const res = await fetch('/fe-api/build').then((res) => res.json());
        const modal: ModalSettings = {
            type: 'component',
            component: 'displayJSONModal',
            title: 'About CISO Assistant',
            body: JSON.stringify(res)
        };
        openState = false;
        modalStore.trigger(modal);
    }

    let enableMoreBtn = $state(false);

    onMount(() => {
        enableMoreBtn = true;
    });

    let openState = $state(false);
</script>

<div class="border-t-2 border-surface-200 pt-4 mt-4">
    <div class="flex flex-row items-center justify-between bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg p-3 shadow-sm">
        <div class="flex flex-col w-3/4">
            {#if page.data.user}
				<span
                        class="text-surface-900 text-sm font-semibold whitespace-nowrap overflow-hidden truncate w-full"
                        data-testid="sidebar-user-name-display"
                >
					{page.data.user.first_name}
                    {page.data.user.last_name}
				</span>
                <span
                        class="font-normal text-xs whitespace-nowrap truncate text-surface-600 mr-2 w-full"
                        data-testid="sidebar-user-email-display"
                >
					{page.data.user.email}
				</span>
            {/if}
        </div>
        {#if enableMoreBtn}
            <Popover
                    open={openState}
                    onOpenChange={(e) => (openState = e.open)}
                    positioning={{ placement: 'top' }}
                    triggerBase="btn "
                    contentBase="card whitespace-nowrap bg-white py-2 w-fit shadow-2xl border-2 border-primary-200 space-y-1 rounded-xl"
                    zIndex="1000"
            >
                {#snippet trigger()}
                    <button class="btn bg-primary-100 hover:bg-primary-200 text-primary-700 transition-all rounded-lg" data-testid="sidebar-more-btn" id="sidebar-more-btn">
                        <i class="fa-solid fa-ellipsis-vertical"></i>
                    </button>
                {/snippet}
                {#snippet content()}
                    <div data-testid="sidebar-more-panel">
                        <a
                                href="/my-profile"
                                onclick={(e) => {
								window.location.href = e.target.href;
							}}
                                class="unstyled cursor-pointer flex items-center gap-3 w-full px-4 py-2.5 text-left text-sm hover:bg-primary-50 disabled:text-surface-400 text-surface-900 rounded-lg transition-all"
                                data-testid="profile-button"
                        ><i class="fa-solid fa-user-circle text-lg text-primary-600"></i><span class="font-medium">{m.myProfile()}</span></a
                        >
                        <select
                                {value}
                                onchange={handleLocaleChange}
                                class="border border-surface-200 focus:border-primary-400 w-full px-4 py-2.5 cursor-pointer block text-sm text-surface-900 bg-white hover:bg-primary-50 focus:ring-2 focus:ring-primary-200 rounded-lg transition-all"
                                data-testid="language-select"
                        >
                            {#each locales as lang}
                                <option value={lang} selected={lang === getLocale()}>
                                    {defaultLangLabels[lang]} ({language[LOCALE_MAP[lang].name]})
                                </option>
                            {/each}
                        </select>
                        <button
                                onclick={() => dispatch('triggerGT')}
                                class="cursor-pointer flex items-center gap-3 w-full px-4 py-2.5 text-left text-sm hover:bg-primary-50 disabled:text-surface-400 text-surface-900 rounded-lg transition-all"
                                data-testid="gt-button"
                        ><i class="fa-solid fa-wand-magic-sparkles text-lg text-primary-600"></i><span class="font-medium">{m.guidedTour()}</span></button
                        >
                        <button
                                onclick={() => dispatch('loadDemoDomain')}
                                class="cursor-pointer flex items-center gap-3 w-full px-4 py-2.5 text-left text-sm hover:bg-secondary-50 disabled:text-surface-400 text-surface-900 rounded-lg transition-all"
                                data-testid="load-demo-data-button"
                        ><i class="fa-solid fa-download text-lg text-secondary-600"></i><span class="font-medium">{m.loadDemoData()}</span></button
                        >
                        <button
                                onclick={modalBuildInfo}
                                class="cursor-pointer flex items-center gap-3 w-full px-4 py-2.5 text-left text-sm hover:bg-tertiary-50 disabled:text-surface-400 text-surface-900 rounded-lg transition-all"
                                data-testid="about-button"
                        ><i class="fa-solid fa-circle-info text-lg text-tertiary-600"></i><span class="font-medium">{m.aboutCiso()}</span></button
                        >
                        <a
                                href="https://intuitem.gitbook.io/ciso-assistant"
                                target="_blank"
                                class="unstyled cursor-pointer flex items-center gap-3 w-full px-4 py-2.5 text-left text-sm hover:bg-primary-50 disabled:text-surface-400 text-surface-900 rounded-lg transition-all"
                                data-testid="docs-button"><i class="fa-solid fa-book text-lg text-primary-600"></i><span class="font-medium">{m.onlineDocs()}</span></a
                        >
                        <div class="border-t border-surface-200 my-2"></div>
                        <form action="/logout" method="POST">
                            <button class="w-full" type="submit" data-testid="logout-button">
								<span
                                        class="flex items-center gap-3 w-full px-4 py-2.5 text-left text-sm hover:bg-error-50 disabled:text-surface-400 text-error-700 rounded-lg transition-all font-medium"
                                ><i class="fa-solid fa-right-from-bracket text-lg text-error-600"></i>{m.Logout()}</span
                                >
                            </button>
                        </form>
                    </div>
                {/snippet}
            </Popover>
        {:else}
            <button
                    class="btn bg-primary-100 text-primary-700 rounded-lg"
                    data-testid="sidebar-more-btn-disabled"
                    id="sidebar-more-btn-disabled"><i class="fa-solid fa-ellipsis-vertical"></i></button
            >
        {/if}
    </div>
</div>
