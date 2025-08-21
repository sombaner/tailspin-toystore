<script lang="ts">
  type Stats = { chunks: number; totalBytes: number };

  let mb = 1;
  let count = 1;
  let stats: Stats | null = null;
  let loading = false;
  let error: string | null = null;
  let note: string | null = null;

  const fmtBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    const units = ['KB', 'MB', 'GB', 'TB'];
    let i = -1;
    do {
      bytes = bytes / 1024;
      i++;
    } while (bytes >= 1024 && i < units.length - 1);
    return `${bytes.toFixed(2)} ${units[i]}`;
  };

  async function refreshStats() {
    loading = true; error = null; note = null;
    try {
      const res = await fetch('/api/debug/leak/stats');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      stats = await res.json();
    } catch (e: any) {
      error = `Failed to load stats. Make sure debug endpoints are enabled on the server (ENABLE_DEBUG_ENDPOINTS=true). ${e?.message ?? e}`;
    } finally { loading = false; }
  }

  async function induce() {
    loading = true; error = null; note = null;
    try {
      const params = new URLSearchParams({ mb: String(mb), count: String(count) });
      const res = await fetch(`/api/debug/leak?${params.toString()}`, { method: 'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      stats = { chunks: data.chunks, totalBytes: data.totalBytes };
      note = `Allocated ${count} x ${mb}MB. Total: ${fmtBytes(stats.totalBytes)}`;
    } catch (e: any) {
      error = `Failed to induce leak: ${e?.message ?? e}`;
    } finally { loading = false; }
  }

  async function clearLeak() {
    loading = true; error = null; note = null;
    try {
      const res = await fetch('/api/debug/leak/clear', { method: 'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      stats = { chunks: data.chunks, totalBytes: data.totalBytes };
      note = 'Cleared retained memory.';
    } catch (e: any) {
      error = `Failed to clear: ${e?.message ?? e}`;
    } finally { loading = false; }
  }

  // Load initial stats on mount
  refreshStats();
</script>

<div class="max-w-3xl mx-auto p-4">
  <div class="bg-slate-800 text-white rounded-lg shadow p-4 border border-slate-700">
    <h2 class="text-xl font-semibold mb-2">Memory Leak Tool</h2>
    <p class="text-sm text-slate-300 mb-4">
      Caution: For testing only. Enable on server with <code class="bg-slate-700 px-1 py-0.5 rounded">ENABLE_DEBUG_ENDPOINTS=true</code>.
    </p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
      <label class="flex flex-col">
        <span class="text-sm text-slate-300 mb-1">MB per allocation</span>
        <input type="number" min="1" bind:value={mb} class="bg-slate-700 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </label>
      <label class="flex flex-col">
        <span class="text-sm text-slate-300 mb-1">Count</span>
        <input type="number" min="1" bind:value={count} class="bg-slate-700 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </label>
      <div class="flex items-end gap-2">
        <button on:click={induce} disabled={loading} class="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded px-4 py-2">Induce</button>
        <button on:click={refreshStats} disabled={loading} class="bg-slate-600 hover:bg-slate-500 disabled:opacity-50 text-white rounded px-4 py-2">Refresh</button>
        <button on:click={clearLeak} disabled={loading} class="bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white rounded px-4 py-2">Clear</button>
      </div>
    </div>

    {#if error}
      <div class="bg-red-900/50 text-red-300 border border-red-800 rounded p-3 mb-3">{error}</div>
    {/if}
    {#if note}
      <div class="bg-green-900/40 text-green-300 border border-green-800 rounded p-3 mb-3">{note}</div>
    {/if}

    <div class="bg-slate-900 rounded p-3 border border-slate-700">
      <h3 class="text-lg font-medium mb-2">Current Stats</h3>
      {#if stats}
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-slate-800 rounded p-3">
            <div class="text-slate-400 text-sm">Chunks</div>
            <div class="text-xl">{stats.chunks}</div>
          </div>
          <div class="bg-slate-800 rounded p-3">
            <div class="text-slate-400 text-sm">Total Retained</div>
            <div class="text-xl">{fmtBytes(stats.totalBytes)}</div>
          </div>
        </div>
      {:else}
        <div class="text-slate-400">Loading…</div>
      {/if}
    </div>
  </div>
</div>

<style>
  :global(html) { color-scheme: dark; }
</style>
