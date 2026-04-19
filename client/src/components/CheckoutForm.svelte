<script lang="ts">
    import { createEventDispatcher } from "svelte";

    export let sessionId = "";
    export let total = 0;

    const dispatch = createEventDispatcher();

    type PaymentMethod = "credit_card" | "debit_card" | "paypal";

    let paymentMethod: PaymentMethod = "credit_card";
    let cardLastFour = "";
    let processing = false;
    let error: string | null = null;
    let success = false;
    let transactionId = "";

    const paymentOptions: { value: PaymentMethod; label: string }[] = [
        { value: "credit_card", label: "Credit Card" },
        { value: "debit_card", label: "Debit Card" },
        { value: "paypal", label: "PayPal" },
    ];

    $: isCardMethod = paymentMethod === "credit_card" || paymentMethod === "debit_card";
    $: canSubmit = !processing && (isCardMethod ? cardLastFour.length === 4 : true);

    const handleSubmit = async () => {
        processing = true;
        error = null;
        try {
            const body: Record<string, string> = {
                session_id: sessionId,
                payment_method: paymentMethod,
            };
            if (isCardMethod) body.card_last_four = cardLastFour;

            const res = await fetch("/api/checkout", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            const data = await res.json();
            if (res.ok) {
                success = true;
                transactionId = data.transactionId ?? data.transaction_id ?? "";
                window.dispatchEvent(new CustomEvent("cart-updated"));
            } else {
                error = data.error ?? "Payment failed. Please try again.";
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            processing = false;
        }
    };
</script>

<div data-testid="checkout-form">
    {#if success}
        <div class="bg-green-600/20 border border-green-500/50 rounded-xl p-8 text-center" data-testid="payment-success">
            <span class="text-5xl mb-4 block">✅</span>
            <h2 class="text-2xl font-bold text-green-400 mb-2">Payment successful!</h2>
            {#if transactionId}
                <p class="text-slate-300">Transaction ID: <span class="font-mono text-slate-100">{transactionId}</span></p>
            {/if}
            <a
                href="/"
                class="inline-block mt-6 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-all duration-300"
            >
                Continue Shopping
            </a>
        </div>
    {:else}
        <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
            <div class="flex items-center justify-between mb-6">
                <h2 class="text-2xl font-bold text-slate-100">Checkout</h2>
                <button
                    on:click={() => dispatch("back")}
                    class="text-slate-400 hover:text-slate-200 transition-colors text-sm"
                >
                    ← Back to cart
                </button>
            </div>

            <div class="mb-6 bg-slate-900/60 rounded-lg border border-slate-700/50 p-4">
                <p class="text-slate-300">Order Total: <span class="text-xl font-bold text-slate-100">${total.toFixed(2)}</span></p>
            </div>

            <div class="space-y-5">
                <div>
                    <label for="payment-method" class="block text-sm font-medium text-slate-300 mb-2">Payment Method</label>
                    <select
                        id="payment-method"
                        bind:value={paymentMethod}
                        class="w-full px-4 py-3 bg-slate-900/60 border border-slate-700/50 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all duration-300"
                        data-testid="payment-method"
                    >
                        {#each paymentOptions as opt}
                            <option value={opt.value}>{opt.label}</option>
                        {/each}
                    </select>
                </div>

                {#if isCardMethod}
                    <div>
                        <label for="card-last-four" class="block text-sm font-medium text-slate-300 mb-2">Card Last 4 Digits</label>
                        <input
                            id="card-last-four"
                            type="text"
                            bind:value={cardLastFour}
                            maxlength="4"
                            pattern="[0-9]{4}"
                            placeholder="1234"
                            class="w-full px-4 py-3 bg-slate-900/60 border border-slate-700/50 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all duration-300"
                            data-testid="card-last-four"
                        />
                    </div>
                {/if}

                {#if error}
                    <div class="bg-red-500/20 border border-red-500/50 text-red-400 rounded-lg p-3 text-sm">
                        {error}
                    </div>
                {/if}

                <button
                    on:click={handleSubmit}
                    disabled={!canSubmit}
                    class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-all duration-300 flex items-center justify-center gap-2"
                    data-testid="pay-button"
                >
                    {#if processing}
                        <span class="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></span>
                        Processing...
                    {:else}
                        Pay ${total.toFixed(2)}
                    {/if}
                </button>
            </div>
        </div>
    {/if}
</div>
