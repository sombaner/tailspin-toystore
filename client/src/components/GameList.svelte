<script lang="ts">
    import { onMount } from "svelte";
    import GameCard from "./GameCard.svelte";
    import LoadingSkeleton from "./LoadingSkeleton.svelte";
    import ErrorMessage from "./ErrorMessage.svelte";
    import EmptyState from "./EmptyState.svelte";

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher_name?: string;
        category_name?: string;
        starRating?: number;
        popularity?: number;
        releaseDate?: string;
    }

    let { games = $bindable([]) }: { games?: Game[] } = $props();
    let loading = $state(true);
    let error = $state<string | null>(null);
    let searchQuery = $state('');
    let sortOption = $state('');
    let searchTimeout: ReturnType<typeof setTimeout> | null = null;

    const sortOptions = [
        { value: '', label: 'Default' },
        { value: 'popularity', label: 'Popularity' },
        { value: 'release_date', label: 'Release Date' },
        { value: 'rating', label: 'User Rating' },
        { value: 'title', label: 'Title' },
    ];

    const fetchGames = async (search: string = '', sort: string = '') => {
        loading = true;
        error = null;
        try {
            const params = new URLSearchParams();
            if (search) params.set('search', search);
            if (sort) params.set('sort', sort);

            const queryString = params.toString();
            const url = queryString ? `/api/games?${queryString}` : '/api/games';
            const response = await fetch(url);
            if(response.ok) {
                games = await response.json();
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const handleSearch = () => {
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }

        searchTimeout = setTimeout(() => {
            fetchGames(searchQuery, sortOption);
        }, 300);
    };

    const handleSort = () => {
        fetchGames(searchQuery, sortOption);
    };

    onMount(() => {
        fetchGames();

        return () => {
            if (searchTimeout) {
                clearTimeout(searchTimeout);
            }
        };
    });
</script>

<div>
    <h2 class="text-2xl font-medium mb-6 text-slate-100">Featured Games</h2>

    <div class="mb-6">
        <div class="flex flex-col sm:flex-row gap-4">
            <div class="relative flex-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                </svg>
                <input
                    type="text"
                    bind:value={searchQuery}
                    oninput={handleSearch}
                    placeholder="Search featured games..."
                    class="w-full pl-10 pr-4 py-3 bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-xl text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all duration-300"
                    data-testid="game-search-input"
                />
            </div>
            <div class="relative">
                <select
                    bind:value={sortOption}
                    onchange={handleSort}
                    class="appearance-none w-full sm:w-48 px-4 py-3 bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-xl text-slate-100 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all duration-300 cursor-pointer"
                    data-testid="game-sort-select"
                >
                    {#each sortOptions as option}
                        <option value={option.value}>{option.label}</option>
                    {/each}
                </select>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
            </div>
        </div>
    </div>
    
    {#if loading}
        <LoadingSkeleton count={6} />
    {:else if error}
        <ErrorMessage error={error} />
    {:else if games.length === 0}
        <EmptyState message="No games available at the moment." />
    {:else}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="games-grid">
            {#each games as game (game.id)}
                <GameCard {game} />
            {/each}
        </div>
    {/if}
</div>