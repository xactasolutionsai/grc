<script lang="ts">
    import { run } from 'svelte/legacy';

    import SuperForm from '$lib/components/Forms/Form.svelte';
    import TextField from '$lib/components/Forms/TextField.svelte';
    import { loginSchema } from '$lib/utils/schemas';

    import { page } from '$app/state';
    import { redirectToProvider } from '$lib/allauth.js';
    import { zod } from 'sveltekit-superforms/adapters';
    import MfaAuthenticateModal from './mfa/components/MFAAuthenticateModal.svelte';
    import { m } from '$paraglide/messages';
    import {
        getModalStore,
        type ModalComponent,
        type ModalSettings,
        type ModalStore
    } from '$lib/components/Modals/stores';

    interface Props {
        data: any;
        form: any;
    }

    let { data, form }: Props = $props();

    const modalStore: ModalStore = getModalStore();

    function modalMFAAuthenticate(): void {
        const modalComponent: ModalComponent = {
            ref: MfaAuthenticateModal,
            props: {
                _form: data.mfaAuthenticateForm,
                formAction: '?/mfaAuthenticate'
            }
        };
        const modal: ModalSettings = {
            type: 'component',
            component: modalComponent,
            // Data
            title: m.mfaAuthenticateTitle(),
            body: m.enterCodeGeneratedByApp()
        };
        modalStore.trigger(modal);
    }

    run(() => {
        form && form.mfaFlow ? modalMFAAuthenticate() : null;
    });
</script>

<div class="flex flex-col w-7/8 lg:w-3/4 p-10 rounded-2xl shadow-2xl bg-white/95 backdrop-blur-lg border-2 border-white/50">
    <div data-testid="login" class="flex flex-col w-full items-center space-y-5">
        <div class="bg-gradient-to-br from-primary-500 via-primary-600 to-secondary-600 px-7 py-6 rounded-2xl text-4xl text-white shadow-xl">
            <i class="fa-solid fa-shield-halved"></i>
        </div>
        <h3
                class="font-bold leading-tight tracking-tight text-3xl bg-gradient-to-r from-secondary-600 via-primary-600 to-tertiary-500 bg-clip-text text-transparent"
        >
            {m.logIntoYourAccount()}
        </h3>
        <p class="text-center text-surface-600 text-base">
            {m.youNeedToLogIn()}
        </p>
        <div class="w-full">
            <!-- SuperForm with dataType 'form' -->
            <SuperForm
                    class="flex flex-col space-y-3"
                    data={data?.form}
                    dataType="form"
                    validators={zod(loginSchema)}
                    action="?/login&next={page.url.searchParams.get('next') || '/'}"
            >
                {#snippet children({ form })}
                    <TextField type="email" {form} field="username" label={m.email()} />
                    <TextField type="password" {form} field="password" label={m.password()} />
                    <div class="flex flex-row justify-end">
                        <a
                                href="/password-reset"
                                class="flex items-center space-x-2 text-primary-800 hover:text-primary-600"
                                data-testid="forgot-password-btn"
                        >
                            <p class="">{m.forgtPassword()}?</p>
                        </a>
                    </div>
                    <p class="">
                        <button
                                class="btn preset-filled-primary-500 font-semibold w-full"
                                data-testid="login-btn"
                                type="submit">{m.login()}</button
                        >
                    </p>
                {/snippet}
            </SuperForm>
        </div>
        {#if data.SSOInfo.is_enabled}
            <div class="flex items-center justify-center w-full space-x-3">
                <hr class="w-64 items-center bg-surface-300 border-0 h-px" />
                <span class="flex items-center text-surface-500 text-sm font-medium">{m.or()}</span>
                <hr class="w-64 items-center bg-surface-300 border-0 h-px" />
            </div>
            <button
                    class="btn bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 text-white font-bold w-1/2 shadow-lg hover:shadow-xl hover:scale-105 transition-all rounded-xl py-3"
                    onclick={() =>
					redirectToProvider(data.SSOInfo.sp_entity_id, data.SSOInfo.callback_url, 'login')}
            >{m.loginSSO()}</button
            >
        {/if}
    </div>
</div>
