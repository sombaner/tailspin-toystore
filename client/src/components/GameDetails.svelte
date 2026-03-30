<script lang="ts">
    import { onMount } from "svelte";
    import ReviewSection from "./ReviewSection.svelte";
    
    interface Game {
        id: number;
        title: string;
        description: string;
        publisher: {
            id: number;
            name: string;
        } | null;
        category: {
            id: number;
            name: string;
        } | null;
        starRating: number | null;
    }

    // Accept either a game object or a gameId
    export let game: Game | undefined = undefined;
    export let gameId = 0;
    
    let loading = true;
    let error: string | null = null;
    let gameData: Game | null = null;
    
    onMount(async () => {
        // If game object is provided directly, use it
        if (game) {
            gameData = game;
            loading = false;
            return;
        }
        
        // Otherwise fetch data using gameId
        if (gameId) {
            try {
                const response = await fetch(`/api/games/${gameId}`);
                if (response.ok) {
                    gameData = await response.json();
                } else {
                    error = `Failed to fetch game: ${response.status} ${response.statusText}`;
                }
            } catch (err) {
                error = `Error: ${err instanceof Error ? err.message : String(err)}`;
            } finally {
                loading = false;
            }
        } else {
            error = "No game ID provided";
            loading = false;
        }
    });

    // Function to render stars based on rating
    function renderStarRating(rating: number | null): string {
        if (rating === null) return "Not yet rated";
        
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
        
        return '★'.repeat(fullStars) + (halfStar ? '½' : '') + '☆'.repeat(emptyStars);
    }

    interface Comment {
        id: number;
        text: string;
    }

    let showSupportForm = false;
    let supportComment = '';
    let comments: Comment[] = [];
    let nextCommentId = 1;

    function submitComment(): void {
        const trimmed = supportComment.trim();
        if (!trimmed) return;
        comments = [...comments, { id: nextCommentId++, text: trimmed }];
        supportComment = '';
    }

    function deleteComment(id: number): void {
        comments = comments.filter(c => c.id !== id);
    }
</script>

{#if loading}
    <div class="animate-pulse bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden p-6">
        <div class="h-8 bg-slate-700 rounded w-1/2 mb-6"></div>
        <div class="h-4 bg-slate-700 rounded w-3/4 mb-3"></div>
        <div class="h-4 bg-slate-700 rounded w-1/2 mb-3"></div>
        <div class="h-4 bg-slate-700 rounded w-full mb-3"></div>
    </div>
{:else if error}
    <div class="bg-red-500/20 border border-red-500/50 text-red-400 rounded-xl p-6">
        {error}
    </div>
{:else if gameData}
    <div class="bg-slate-800/70 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden" data-testid="game-details">
        <div class="p-6">
            <div class="flex justify-between items-start flex-wrap gap-3">
                <h1 class="text-3xl font-bold text-slate-100 mb-2" data-testid="game-details-title">{gameData.title}</h1>
                
                {#if gameData.starRating !== null}
                <div class="flex items-center">
                    <span class="bg-blue-500/20 text-blue-400 text-sm px-3 py-1 rounded-full" data-testid="game-rating">
                        <span class="text-yellow-400">{renderStarRating(gameData.starRating)}</span> 
                        {gameData.starRating.toFixed(1)}
                    </span>
                </div>
                {/if}
            </div>
            
            <div class="flex flex-wrap gap-2 mt-4 mb-6">
                {#if gameData.category}
                    <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-blue-900/60 text-blue-300" data-testid="game-details-category">
                        {gameData.category.name}
                    </span>
                {/if}
                {#if gameData.publisher}
                    <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-purple-900/60 text-purple-300" data-testid="game-details-publisher">
                        {gameData.publisher.name}
                    </span>
                {/if}
            </div>
            
            <div class="space-y-4 mt-6">
                <h2 class="text-lg font-semibold text-slate-200 mb-2">About this game</h2>
                <div class="text-slate-400 space-y-4">
                    <p data-testid="game-details-description">{gameData.description}</p>
                </div>
            </div>
            
            <div class="mt-8">
                <button 
                    on:click={() => showSupportForm = !showSupportForm}
                    class="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 flex justify-center items-center" 
                    data-testid="back-game-button"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                    </svg>
                    Support This Game
                </button>
                
                {#if showSupportForm}
                    <div class="mt-4 bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4 transition-all duration-300" data-testid="support-comment-section">
                        <label for="support-comment" class="block text-sm font-medium text-slate-300 mb-2">
                            Why do you want to support this game?
                        </label>
                        <textarea
                            id="support-comment"
                            bind:value={supportComment}
                            placeholder="Share your thoughts on why this game deserves support..."
                            rows="4"
                            class="w-full bg-slate-900/60 border border-slate-700/50 rounded-lg text-slate-100 placeholder-slate-400 p-3 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all duration-300 resize-none"
                            data-testid="support-comment-input"
                        ></textarea>
                        <div class="flex gap-3 mt-3">
                            <button
                                on:click={submitComment}
                                disabled={!supportComment.trim()}
                                class="bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition-all duration-300"
                                data-testid="support-comment-submit"
                            >
                                Submit
                            </button>
                        </div>
                    </div>

                    {#if comments.length > 0}
                        <div class="mt-4 space-y-3" data-testid="support-comments-list">
                            <h3 class="text-sm font-semibold text-slate-300">Support Comments</h3>
                            {#each comments as comment (comment.id)}
                                <div class="flex items-start justify-between gap-3 bg-slate-900/60 border border-slate-700/50 rounded-lg p-3" data-testid="support-comment-item">
                                    <p class="text-slate-300 text-sm flex-1" data-testid="support-comment-text">{comment.text}</p>
                                    <button
                                        on:click={() => deleteComment(comment.id)}
                                        class="text-red-400 hover:text-red-300 hover:bg-red-500/20 p-1 rounded transition-all duration-200 shrink-0"
                                        data-testid="support-comment-delete"
                                        aria-label="Delete comment"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                                        </svg>
                                    </button>
                                </div>
                            {/each}
                        </div>
                    {/if}
                {/if}
            </div>

            <ReviewSection gameId={gameData.id} />
        </div>
    </div>
{:else}
    <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6">
        <p class="text-slate-400">No game information available</p>
    </div>
{/if}