<script lang="ts">
    import { onMount } from "svelte";

    let count = 0;
    let loading = true;

    function getSessionId(): string {
        if (typeof localStorage === "undefined") return "";
        let id = localStorage.getItem("cartSessionId");
        if (!id) {
            id = crypto.randomUUID();
            localStorage.setItem("cartSessionId", id);
        }
        return id;
    }

    const fetchCount = async () => {
        try {
            const sessionId = getSessionId();
            if (!sessionId) return;
            const res = await fetch(`/api/cart/count?session_id=${sessionId}`);
            if (res.ok) {
                const data = await res.json();
                count = data.count ?? 0;
            }
        } catch {
            count = 0;
        } finally {
            loading = false;
        }
    };

    onMount(() => {
        fetchCount();
        // Listen for cart updates from other components
        window.addEventListener("cart-updated", () => fetchCount());
        return () => window.removeEventListener("cart-updated", () => fetchCount());
    });
</script>

<a
    href="/cart"
    class="relative inline-flex items-center text-white hover:text-blue-200 transition-colors duration-200 p-2"
    data-testid="cart-button"
    aria-label="Shopping cart"
>
    <span class="text-xl">🛒</span>
    {#if !loading && count > 0}
        <span
            class="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center"
            data-testid="cart-count"
        >
            {count > 99 ? "99+" : count}
        </span>
    {/if}
</a>
