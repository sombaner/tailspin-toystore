<script lang="ts">
    import { onMount } from "svelte";
    import CheckoutForm from "./CheckoutForm.svelte";

    interface CartItem {
        id: number;
        gameId: number;
        gameTitle: string;
        quantity: number;
        price: number;
        subtotal: number;
    }

    interface Cart {
        items: CartItem[];
        total: number;
    }

    let cart: Cart = { items: [], total: 0 };
    let loading = true;
    let error: string | null = null;
    let showCheckout = false;
    let updatingItems: Set<number> = new Set();

    function getSessionId(): string {
        if (typeof localStorage === "undefined") return "";
        let id = localStorage.getItem("cartSessionId");
        if (!id) {
            id = crypto.randomUUID();
            localStorage.setItem("cartSessionId", id);
        }
        return id;
    }

    function dispatchCartUpdate(): void {
        window.dispatchEvent(new CustomEvent("cart-updated"));
    }

    const fetchCart = async () => {
        try {
            const sessionId = getSessionId();
            if (!sessionId) { error = "No session"; loading = false; return; }
            const res = await fetch(`/api/cart?session_id=${sessionId}`);
            if (res.ok) {
                cart = await res.json();
            } else {
                error = `Failed to load cart: ${res.status} ${res.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const updateQuantity = async (itemId: number, newQuantity: number) => {
        if (newQuantity < 1) return;
        updatingItems = new Set([...updatingItems, itemId]);
        try {
            const res = await fetch(`/api/cart/items/${itemId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ quantity: newQuantity, session_id: getSessionId() }),
            });
            if (res.ok) {
                await fetchCart();
                dispatchCartUpdate();
            }
        } catch {
            // silently fail, cart stays as-is
        } finally {
            updatingItems.delete(itemId);
            updatingItems = updatingItems;
        }
    };

    const removeItem = async (itemId: number) => {
        updatingItems = new Set([...updatingItems, itemId]);
        try {
            const res = await fetch(`/api/cart/items/${itemId}?session_id=${getSessionId()}`, {
                method: "DELETE",
            });
            if (res.ok) {
                await fetchCart();
                dispatchCartUpdate();
            }
        } catch {
            // silently fail
        } finally {
            updatingItems.delete(itemId);
            updatingItems = updatingItems;
        }
    };

    onMount(() => {
        fetchCart();
    });
</script>

<div data-testid="cart-page">
    <h1 class="text-3xl font-bold text-slate-100 mb-8">Your Cart</h1>

    {#if loading}
        <div class="space-y-4">
            {#each Array(3) as _}
                <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
                    <div class="animate-pulse flex items-center justify-between">
                        <div class="flex-1">
                            <div class="h-5 bg-slate-700 rounded w-1/3 mb-3"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/4"></div>
                        </div>
                        <div class="h-8 bg-slate-700 rounded w-24"></div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if error}
        <div class="bg-red-500/20 border border-red-500/50 text-red-400 rounded-xl p-6">
            {error}
        </div>
    {:else if cart.items.length === 0}
        <div class="text-center py-16 bg-slate-800/60 backdrop-blur-sm rounded-xl border border-slate-700/50">
            <span class="text-5xl mb-4 block">🛒</span>
            <p class="text-slate-300 text-lg mb-6">Your cart is empty</p>
            <a
                href="/"
                class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-all duration-300"
            >
                Browse Games
            </a>
        </div>
    {:else}
        {#if !showCheckout}
            <div class="space-y-4">
                {#each cart.items as item (item.id)}
                    <div
                        class="bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50 p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                        data-testid="cart-item"
                    >
                        <div class="flex-1 min-w-0">
                            <h3 class="text-lg font-semibold text-slate-100 truncate">{item.gameTitle}</h3>
                            <p class="text-slate-400 text-sm">${item.price.toFixed(2)} each</p>
                        </div>

                        <div class="flex items-center gap-3">
                            <div class="flex items-center bg-slate-900/60 rounded-lg border border-slate-700/50">
                                <button
                                    on:click={() => updateQuantity(item.id, item.quantity - 1)}
                                    disabled={item.quantity <= 1 || updatingItems.has(item.id)}
                                    class="px-3 py-1.5 text-slate-300 hover:text-white hover:bg-slate-700/50 rounded-l-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                                    aria-label="Decrease quantity"
                                >−</button>
                                <span class="px-3 py-1.5 text-slate-100 font-medium min-w-[2rem] text-center">{item.quantity}</span>
                                <button
                                    on:click={() => updateQuantity(item.id, item.quantity + 1)}
                                    disabled={updatingItems.has(item.id)}
                                    class="px-3 py-1.5 text-slate-300 hover:text-white hover:bg-slate-700/50 rounded-r-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                                    aria-label="Increase quantity"
                                >+</button>
                            </div>

                            <span class="text-slate-100 font-semibold w-20 text-right">${item.subtotal.toFixed(2)}</span>

                            <button
                                on:click={() => removeItem(item.id)}
                                disabled={updatingItems.has(item.id)}
                                class="bg-red-600 hover:bg-red-700 text-white p-2 rounded-lg transition-all duration-300 disabled:opacity-40"
                                aria-label="Remove item"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                                </svg>
                            </button>
                        </div>
                    </div>
                {/each}
            </div>

            <div class="mt-6 bg-slate-800/60 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div class="text-xl font-bold text-slate-100" data-testid="cart-total">
                    Total: ${cart.total.toFixed(2)}
                </div>
                <button
                    on:click={() => showCheckout = true}
                    class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-8 rounded-lg transition-all duration-300"
                    data-testid="checkout-button"
                >
                    Proceed to Checkout
                </button>
            </div>
        {:else}
            <CheckoutForm
                sessionId={getSessionId()}
                total={cart.total}
                on:back={() => showCheckout = false}
            />
        {/if}
    {/if}
</div>
