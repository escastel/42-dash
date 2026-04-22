<template>
  <div class="home-view">
    <div class="container">
      <h1 class="page-title">Game Catalog</h1>

      <div class="controls-section">
        <div class="search-box">
          <input
            v-model="searchInput"
            type="text"
            placeholder="Search games..."
            data-testid="search-input"
            aria-label="Search for games"
            @input="handleSearch"
          />
        </div>

        <div class="filters">
          <div class="filter-group">
            <label for="category-select">Category</label>
            <select
              id="category-select"
              v-model="selectedCategory"
              data-testid="category-filter"
              @change="handleFilterChange"
            >
              <option value="">All Categories</option>
              <option value="slots">Slots</option>
              <option value="live">Live</option>
              <option value="table">Table</option>
              <option value="instant">Instant</option>
              <option value="jackpot">Jackpot</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="provider-select">Provider</label>
            <select
              id="provider-select"
              v-model="selectedProvider"
              data-testid="provider-filter"
              @change="handleFilterChange"
            >
              <option value="">All Providers</option>
              <option v-for="p in providers" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="enabled-select">Status</label>
            <select
              id="enabled-select"
              v-model="selectedEnabled"
              @change="handleFilterChange"
            >
              <option value="">All</option>
              <option value="true">Enabled</option>
              <option value="false">Disabled</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state" data-testid="loading">
        <div class="spinner"></div>
        <p>Loading games...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <h2>Something went wrong</h2>
        <p>{{ error }}</p>
        <button @click="loadGames">Retry</button>
      </div>

      <div v-else-if="games.length === 0" class="empty-state" data-testid="empty-state">
        <p>No games found. Try adjusting your filters.</p>
      </div>

      <div v-else class="games-grid">
        <game-card
          v-for="game in games"
          :key="game.id"
          :game="game"
          @click="goToGame(game.id)"
        />
      </div>

      <div v-if="meta && meta.totalPages > 1" class="pagination">
        <button
          :disabled="currentPage === 1"
          @click="previousPage"
          aria-label="Previous page"
        >
          ← Previous
        </button>

        <div class="page-info">
          Page {{ currentPage }} of {{ meta.totalPages }}
        </div>

        <button
          :disabled="currentPage === meta.totalPages"
          @click="nextPage"
          aria-label="Next page"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { gameService } from '../api.js'
import GameCard from '../components/GameCard.vue'

export default {
  name: 'HomeView',
  components: { GameCard },
  setup() {
    const router = useRouter()
    const route = useRoute()

    const games = ref([])
    const loading = ref(false)
    const error = ref(null)
    const meta = ref(null)
    const providers = ref([])

    const searchInput = ref('')
    const selectedCategory = ref('')
    const selectedProvider = ref('')
    const selectedEnabled = ref('')
    const currentPage = ref(1)
    const pageSize = 20

    // Initialize from URL params
    function initFromUrl() {
      const query = route.query
      searchInput.value = query.search || ''
      selectedCategory.value = query.category || ''
      selectedProvider.value = query.provider || ''
      selectedEnabled.value = query.enabled || ''
      currentPage.value = parseInt(query.page) || 1
    }

    // Update URL with current filters
    function updateUrl() {
      const query = {}
      if (searchInput.value) query.search = searchInput.value
      if (selectedCategory.value) query.category = selectedCategory.value
      if (selectedProvider.value) query.provider = selectedProvider.value
      if (selectedEnabled.value) query.enabled = selectedEnabled.value
      if (currentPage.value > 1) query.page = currentPage.value

      router.push({ name: 'Home', query })
    }

    // Load games from API
    async function loadGames() {
      loading.value = true
      error.value = null
      
      try {
        const params = {
          search: searchInput.value || undefined,
          category: selectedCategory.value || undefined,
          provider: selectedProvider.value || undefined,
          enabled: selectedEnabled.value ? selectedEnabled.value === 'true' : undefined,
          sort: 'name',
          order: 'asc',
          page: currentPage.value,
          pageSize,
        }

        const response = await gameService.listGames(params)
        games.value = response.data || []
        meta.value = response.meta || {}

        // Extract unique providers
        if (games.value.length > 0 && providers.value.length === 0) {
          const uniqueProviders = new Set()
          games.value.forEach(g => {
            if (g.provider) uniqueProviders.add(g.provider)
          })
          providers.value = Array.from(uniqueProviders).sort()
        }
      } catch (err) {
        error.value = err.message || 'Failed to load games'
        games.value = []
      } finally {
        loading.value = false
      }
    }

    function handleSearch() {
      currentPage.value = 1
      updateUrl()
    }

    function handleFilterChange() {
      currentPage.value = 1
      updateUrl()
    }

    function nextPage() {
      if (meta.value && currentPage.value < meta.value.totalPages) {
        currentPage.value++
        updateUrl()
      }
    }

    function previousPage() {
      if (currentPage.value > 1) {
        currentPage.value--
        updateUrl()
      }
    }

    function goToGame(gameId) {
      router.push(`/games/${gameId}`)
    }

    // Watch URL changes and filters
    watch(() => route.query, () => {
      initFromUrl()
      loadGames()
    }, { deep: true })

    watch([searchInput, selectedCategory, selectedProvider, selectedEnabled, currentPage], () => {
      loadGames()
    })

    onMounted(() => {
      initFromUrl()
      loadGames()
    })

    return {
      games,
      loading,
      error,
      meta,
      providers,
      searchInput,
      selectedCategory,
      selectedProvider,
      selectedEnabled,
      currentPage,
      handleSearch,
      handleFilterChange,
      nextPage,
      previousPage,
      goToGame,
      loadGames,
    }
  },
}
</script>

<style scoped>
.home-view {
  padding: 0 0 4rem 0;
}

.page-title {
  margin-bottom: 2rem;
  text-align: center;
}

.controls-section {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.search-box {
  margin-bottom: 1.5rem;
}

.search-box input {
  width: 100%;
  padding: 0.875rem;
  font-size: 1rem;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.filter-group select {
  width: 100%;
}

.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem 0;
}

.pagination button {
  padding: 0.625rem 1.25rem;
}

.page-info {
  color: var(--text-secondary);
  font-weight: 500;
  min-width: 150px;
  text-align: center;
}

@media (max-width: 768px) {
  .filters {
    grid-template-columns: 1fr;
  }

  .games-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }

  .pagination {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .games-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .controls-section {
    padding: 1rem;
  }
}
</style>
