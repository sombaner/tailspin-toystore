<script lang="ts">
    import { onMount } from "svelte";

    export let gameId: number;

    interface Review {
        id: number;
        gameId: number;
        rating: number;
        reviewText: string;
        reviewerName: string;
        createdAt: string;
    }

    let reviews: Review[] = [];
    let averageRating: number | null = null;
    let totalReviews = 0;
    let loading = true;

    // Rating form state
    let selectedRating = 0;
    let hoveredRating = 0;
    let showReviewForm = false;
    let reviewerName = '';
    let reviewText = '';
    let submitting = false;
    let submitError: string | null = null;
    let submitSuccess = false;

    onMount(() => {
        fetchReviews();
    });

    async function fetchReviews() {
        try {
            const res = await fetch(`/api/games/${gameId}/reviews`);
            if (res.ok) {
                const data = await res.json();
                reviews = data.reviews;
                averageRating = data.averageRating;
                totalReviews = data.totalReviews;
            }
        } catch {
            // silently fail, reviews are non-critical
        } finally {
            loading = false;
        }
    }

    function selectRating(star: number) {
        selectedRating = star;
        showReviewForm = true;
        submitSuccess = false;
        submitError = null;
    }

    async function submitReview() {
        if (!selectedRating || !reviewerName.trim() || !reviewText.trim()) return;

        submitting = true;
        submitError = null;

        try {
            const res = await fetch(`/api/games/${gameId}/reviews`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rating: selectedRating,
                    reviewerName: reviewerName.trim(),
                    reviewText: reviewText.trim(),
                }),
            });

            if (res.ok) {
                submitSuccess = true;
                selectedRating = 0;
                reviewerName = '';
                reviewText = '';
                showReviewForm = false;
                await fetchReviews();
            } else {
                const data = await res.json();
                submitError = data.error || 'Failed to submit review';
            }
        } catch {
            submitError = 'Network error. Please try again.';
        } finally {
            submitting = false;
        }
    }

    function formatDate(iso: string): string {
        return new Date(iso).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    }

    function renderStars(rating: number): string {
        return '★'.repeat(rating) + '☆'.repeat(5 - rating);
    }
</script>

<div class="mt-10" data-testid="review-section">
    <h2 class="text-xl font-bold text-slate-100 mb-4">Ratings & Reviews</h2>

    {#if averageRating !== null}
        <div class="flex items-center gap-3 mb-6" data-testid="review-summary">
            <span class="text-3xl font-bold text-yellow-400">{averageRating}</span>
            <div>
                <span class="text-yellow-400 text-lg">{renderStars(Math.round(averageRating))}</span>
                <p class="text-slate-400 text-sm">{totalReviews} {totalReviews === 1 ? 'review' : 'reviews'}</p>
            </div>
        </div>
    {/if}

    <!-- Star rating selector -->
    <div class="bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-xl p-5 mb-6" data-testid="rating-selector">
        <p class="text-slate-300 text-sm font-medium mb-3">Rate this game</p>
        <div class="flex gap-1">
            {#each [1, 2, 3, 4, 5] as star}
                <button
                    on:click={() => selectRating(star)}
                    on:mouseenter={() => hoveredRating = star}
                    on:mouseleave={() => hoveredRating = 0}
                    class="text-3xl transition-transform duration-150 hover:scale-110 focus:outline-none"
                    class:text-yellow-400={star <= (hoveredRating || selectedRating)}
                    class:text-slate-600={star > (hoveredRating || selectedRating)}
                    data-testid="rating-star-{star}"
                    aria-label="Rate {star} out of 5"
                >
                    ★
                </button>
            {/each}
            {#if selectedRating > 0}
                <span class="ml-2 text-slate-400 text-sm self-center">{selectedRating}/5</span>
            {/if}
        </div>
    </div>

    <!-- Review form (shown after selecting a rating) -->
    {#if showReviewForm}
        <div class="bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-xl p-5 mb-6 transition-all duration-300" data-testid="review-form">
            <h3 class="text-lg font-semibold text-slate-200 mb-4">Write a Review</h3>

            <div class="mb-4">
                <label for="reviewer-name" class="block text-sm font-medium text-slate-300 mb-1">Your Name</label>
                <input
                    id="reviewer-name"
                    type="text"
                    bind:value={reviewerName}
                    placeholder="Enter your name"
                    class="w-full bg-slate-900/60 border border-slate-700/50 rounded-lg text-slate-100 placeholder-slate-500 p-3 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all duration-300"
                    data-testid="reviewer-name-input"
                />
            </div>

            <div class="mb-4">
                <label for="review-text" class="block text-sm font-medium text-slate-300 mb-1">Your Review</label>
                <textarea
                    id="review-text"
                    bind:value={reviewText}
                    placeholder="What did you think about this game? (min 10 characters)"
                    rows="4"
                    class="w-full bg-slate-900/60 border border-slate-700/50 rounded-lg text-slate-100 placeholder-slate-500 p-3 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all duration-300 resize-none"
                    data-testid="review-text-input"
                ></textarea>
            </div>

            {#if submitError}
                <p class="text-red-400 text-sm mb-3" data-testid="review-error">{submitError}</p>
            {/if}

            <div class="flex gap-3">
                <button
                    on:click={submitReview}
                    disabled={submitting || !reviewerName.trim() || reviewText.trim().length < 10}
                    class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium py-2 px-5 rounded-lg transition-all duration-200"
                    data-testid="review-submit-button"
                >
                    {submitting ? 'Submitting...' : 'Submit Review'}
                </button>
                <button
                    on:click={() => { showReviewForm = false; selectedRating = 0; }}
                    class="text-slate-400 hover:text-slate-200 py-2 px-4 rounded-lg transition-all duration-200"
                    data-testid="review-cancel-button"
                >
                    Cancel
                </button>
            </div>
        </div>
    {/if}

    {#if submitSuccess}
        <div class="bg-green-500/20 border border-green-500/50 text-green-400 rounded-xl p-4 mb-6" data-testid="review-success">
            Thank you! Your review has been submitted.
        </div>
    {/if}

    <!-- Reviews list -->
    {#if loading}
        <div class="space-y-4">
            {#each [1, 2] as _}
                <div class="animate-pulse bg-slate-800/60 rounded-xl p-4">
                    <div class="h-4 bg-slate-700 rounded w-1/4 mb-2"></div>
                    <div class="h-3 bg-slate-700 rounded w-full mb-1"></div>
                    <div class="h-3 bg-slate-700 rounded w-3/4"></div>
                </div>
            {/each}
        </div>
    {:else if reviews.length > 0}
        <div class="space-y-4" data-testid="reviews-list">
            {#each reviews as review (review.id)}
                <div class="bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4" data-testid="review-item">
                    <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center gap-2">
                            <span class="text-yellow-400 text-sm">{renderStars(review.rating)}</span>
                            <span class="font-medium text-slate-200 text-sm" data-testid="review-author">{review.reviewerName}</span>
                        </div>
                        <span class="text-slate-500 text-xs">{formatDate(review.createdAt)}</span>
                    </div>
                    <p class="text-slate-300 text-sm" data-testid="review-text">{review.reviewText}</p>
                </div>
            {/each}
        </div>
    {:else}
        <p class="text-slate-500 text-sm">No reviews yet. Be the first to review this game!</p>
    {/if}
</div>
