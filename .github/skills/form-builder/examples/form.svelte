<script lang="ts">
  import { tick } from "svelte";

  export let gameId: number;

  type FieldErrors = Partial<Record<"name" | "email" | "amount" | "message", string>>;

  let form = {
    name: "",
    email: "",
    amount: "",
    message: "",
  };

  let fieldErrors: FieldErrors = {};
  let submitting = false;
  let submitError: string | null = null;
  let submitSuccess = false;

  function validate(): boolean {
    const errors: FieldErrors = {};

    if (!form.name.trim()) errors.name = "Name is required.";
    if (!form.email.trim()) errors.email = "Email is required.";
    if (form.email && !/^\S+@\S+\.\S+$/.test(form.email)) errors.email = "Enter a valid email address.";

    const amountNumber = Number(form.amount);
    if (!form.amount.trim()) errors.amount = "Amount is required.";
    else if (Number.isNaN(amountNumber) || amountNumber <= 0) errors.amount = "Enter an amount greater than 0.";

    if (form.message.length > 500) errors.message = "Message must be 500 characters or less.";

    fieldErrors = errors;
    return Object.keys(errors).length === 0;
  }

  async function focusFirstInvalidField(): Promise<void> {
    await tick();
    const firstKey = Object.keys(fieldErrors)[0];
    if (!firstKey) return;

    const el = document.querySelector<HTMLInputElement | HTMLTextAreaElement>(`[data-field="${firstKey}"]`);
    el?.focus();
  }

  async function onSubmit(e: SubmitEvent): Promise<void> {
    e.preventDefault();

    submitError = null;
    submitSuccess = false;

    if (!validate()) {
      await focusFirstInvalidField();
      return;
    }

    submitting = true;
    try {
      const payload = {
        gameId,
        name: form.name.trim(),
        email: form.email.trim(),
        amount: Number(form.amount),
        message: form.message.trim() || null,
      };

      const response = await fetch("/api/pledges", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        // Optional server shape:
        // { message: string, fieldErrors?: { [key: string]: string } }
        const body = await response.json().catch(() => null);
        submitError =
          body?.message ?? `Failed to submit pledge: ${response.status} ${response.statusText}`;

        if (body?.fieldErrors && typeof body.fieldErrors === "object") {
          fieldErrors = { ...fieldErrors, ...body.fieldErrors };
          await focusFirstInvalidField();
        }

        return;
      }

      submitSuccess = true;
      form = { name: "", email: "", amount: "", message: "" };
      fieldErrors = {};
    } catch (err) {
      submitError = `Error: ${err instanceof Error ? err.message : String(err)}`;
    } finally {
      submitting = false;
    }
  }
</script>

<form
  class="bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50 p-6 space-y-5"
  data-testid="form-support-game"
  on:submit={onSubmit}
>
  <div>
    <h2 class="text-2xl font-semibold text-slate-100">Support this game</h2>
    <p class="text-slate-400 text-sm mt-1">Pledge securely and help fund development.</p>
  </div>

  {#if submitError}
    <div
      class="bg-red-500/20 border border-red-500/50 text-red-400 rounded-xl p-4"
      role="alert"
      data-testid="form-error"
    >
      {submitError}
    </div>
  {/if}

  {#if submitSuccess}
    <div
      class="bg-blue-500/20 border border-blue-500/40 text-blue-300 rounded-xl p-4"
      role="status"
      data-testid="form-success"
    >
      Thanks! Your pledge was submitted.
    </div>
  {/if}

  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
    <div>
      <label class="block text-sm font-medium text-slate-200 mb-1" for="name">Name</label>
      <input
        id="name"
        name="name"
        data-field="name"
        data-testid="field-name"
        class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/50"
        bind:value={form.name}
        aria-invalid={fieldErrors.name ? "true" : "false"}
        aria-describedby={fieldErrors.name ? "name-error" : undefined}
        placeholder="Ada Lovelace"
      />
      {#if fieldErrors.name}
        <p id="name-error" class="mt-1 text-sm text-red-400" data-testid="error-name">
          {fieldErrors.name}
        </p>
      {/if}
    </div>

    <div>
      <label class="block text-sm font-medium text-slate-200 mb-1" for="email">Email</label>
      <input
        id="email"
        name="email"
        type="email"
        data-field="email"
        data-testid="field-email"
        class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/50"
        bind:value={form.email}
        aria-invalid={fieldErrors.email ? "true" : "false"}
        aria-describedby={fieldErrors.email ? "email-error" : undefined}
        placeholder="ada@example.com"
      />
      {#if fieldErrors.email}
        <p id="email-error" class="mt-1 text-sm text-red-400" data-testid="error-email">
          {fieldErrors.email}
        </p>
      {/if}
    </div>
  </div>

  <div>
    <label class="block text-sm font-medium text-slate-200 mb-1" for="amount">Pledge amount</label>
    <input
      id="amount"
      name="amount"
      inputmode="decimal"
      data-field="amount"
      data-testid="field-amount"
      class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/50"
      bind:value={form.amount}
      aria-invalid={fieldErrors.amount ? "true" : "false"}
      aria-describedby={fieldErrors.amount ? "amount-error" : "amount-hint"}
      placeholder="25"
    />
    <p id="amount-hint" class="mt-1 text-xs text-slate-500">Enter a number greater than 0.</p>
    {#if fieldErrors.amount}
      <p id="amount-error" class="mt-1 text-sm text-red-400" data-testid="error-amount">
        {fieldErrors.amount}
      </p>
    {/if}
  </div>

  <div>
    <label class="block text-sm font-medium text-slate-200 mb-1" for="message">Message (optional)</label>
    <textarea
      id="message"
      name="message"
      rows="4"
      data-field="message"
      data-testid="field-message"
      class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/50"
      bind:value={form.message}
      aria-invalid={fieldErrors.message ? "true" : "false"}
      aria-describedby={fieldErrors.message ? "message-error" : undefined}
      placeholder="What excites you about this game?"
    />
    {#if fieldErrors.message}
      <p id="message-error" class="mt-1 text-sm text-red-400" data-testid="error-message">
        {fieldErrors.message}
      </p>
    {/if}
  </div>

  <button
    type="submit"
    data-testid="submit-support-game"
    class="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 flex justify-center items-center disabled:opacity-60 disabled:cursor-not-allowed"
    disabled={submitting}
  >
    {#if submitting}
      <span class="animate-pulse">Submitting…</span>
    {:else}
      Submit pledge
    {/if}
  </button>
</form>