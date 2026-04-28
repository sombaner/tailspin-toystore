---
applyTo: '**/*.svelte,**/*.astro,**/*.css'
---

# UI Instructions

> For full frontend conventions, see `.github/copilot-instructions.md` § Svelte / Astro Frontend Coding.

## Dark Mode Palette

- Background: `bg-slate-900` (page), `bg-slate-800/60` (cards)
- Text: `text-white`, `text-slate-400` (muted)
- Borders: `border-slate-700/50`
- Accents: `bg-blue-600`, `hover:bg-blue-700`
- Cards: `rounded-xl overflow-hidden shadow-lg border border-slate-700/50 backdrop-blur-sm`

## Component States

All data-fetching components must handle:
- **Loading**: `animate-pulse` skeleton with `bg-slate-700` placeholders
- **Error**: user-friendly message with retry option
- **Empty**: descriptive empty state (not blank)

## Interactive Elements

- Buttons: `bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-300`
- Hover lift: `hover:translate-y-[-6px] hover:border-blue-500/50 hover:shadow-blue-500/10`
- Focus states: visible outline for keyboard navigation

## Testing & Accessibility

- Add `data-testid` on key elements (cards, titles, buttons, forms)
- Use semantic HTML (`<nav>`, `<main>`, `<article>`, `<button>`)
- Ensure sufficient color contrast (white on slate-800+ passes WCAG AA)
- Use ARIA attributes where semantic HTML is insufficient

## Layout

- Responsive grids: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`
- No custom CSS except in `global.css` or `<style is:global>`
