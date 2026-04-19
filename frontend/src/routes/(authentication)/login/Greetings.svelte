<script lang="ts">
    import { m } from '$paraglide/messages';
    import Typewriter from 'sv-typewriter';
</script>

<div
        id="hellothere"
        class="flex flex-col justify-center items-center lg:w-3/5 text-white px-4 lg:px-0"
>
    <Typewriter mode="loopOnce" cursor={false} interval={50}>
        <div class="text-3xl unstyled text-center pb-6 font-semibold">
            <span class="text-3xl text-center text-white/90">{m.helloThere()} </span>
            <span class="bg-gradient-to-r from-tertiary-300 to-white bg-clip-text text-transparent"> {m.thisIsCisoAssistant()} </span>
        </div>
    </Typewriter>
    <Typewriter mode="cascade" cursor={false} interval={45} delay={5000}>
        <div class="text-2xl unstyled text-center text-white/80">
            <span> {m.yourStreamlined()} </span>
            <span class="font-black text-tertiary-300"> {m.oneStopShop()} </span>
            <span> {m.forComplianceRiskManagement()} </span>
        </div>
    </Typewriter>
</div>
