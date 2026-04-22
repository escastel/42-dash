<template>
  <div class="game-detail-view">
    <div class="container">
      <button @click="goBack" class="btn-back" aria-label="Go back to catalog">← Back to Catalog</button>

      <div v-if="loading" class="loading-state" aria-busy="true" data-testid="loading">
        <div class="spinner"></div>
        <p>Loading game details...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <h2>Game Not Found</h2>
        <p>{{ error }}</p>
        <router-link to="/" class="btn-home">Return to Catalog</router-link>
      </div>

      <div v-else-if="game" class="game-detail" data-testid="game-detail">
        <div class="detail-header">
          <div class="detail-image">
            <img :src="getGameThumb()" :alt="getGameName()" @error="onImageError" />
          </div>

          <div class="detail-info">
            <h1 class="game-name">{{ getGameName() }}</h1>
            
            <div class="info-grid">
              <div class="info-item">
                <label>Provider</label>
                <p class="info-value">{{ getProvider() }}</p>
              </div>
              <div class="info-item">
                <label>Category</label>
                <p class="info-value">{{ getCategory() }}</p>
              </div>
              <div class="info-item">
                <label>RTP</label>
                <p class="info-value rtp">{{ getRtp() }}%</p>
              </div>
              <div class="info-item">
                <label>Volatility</label>
                <p class="info-value volatility" :class="getVolatilityClass()">{{ getVolatility() }}</p>
              </div>
              <div class="info-item">
                <label>Status</label>
                <p class="info-value" :class="isEnabled() ? 'enabled' : 'disabled'">{{ isEnabled() ? '✓ Enabled' : '✗ Disabled' }}</p>
              </div>
              <div class="info-item">
                <label>Release Date</label>
                <p class="info-value">{{ getFormattedDate() }}</p>
              </div>
            </div>

            <div v-if="getFeatures().length > 0" class="features-section">
              <label>Features</label>
              <div class="features-list">
                <span v-for="feature in getFeatures()" :key="feature" class="feature-tag">{{ formatFeature(feature) }}</span>
              </div>
            </div>

            <div class="actions">
              <router-link v-if="isEnabled()" :to="`/games/${gameId}/launch`" class="btn-launch">🎮 Launch Game</router-link>
              <button v-else class="btn-launch disabled" disabled>Game Disabled</button>
            </div>
          </div>
        </div>

        <div class="stats-section">
          <h2>Game Statistics</h2>
          <div class="stats-grid">
            <div class="stat-card">
              <h3>Return to Player</h3>
              <p class="stat-value">{{ getRtp() }}%</p>
            </div>
            <div class="stat-card">
              <h3>Volatility</h3>
              <p class="stat-value">{{ getVolatility() }}</p>
            </div>
            <div class="stat-card">
              <h3>Provider</h3>
              <p class="stat-value">{{ getProvider() }}</p>
            </div>
            <div class="stat-card">
              <h3>Category</h3>
              <p class="stat-value">{{ getCategory() }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { gameService } from '../api.js'

export default {
  name: 'GameDetailView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const game = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const gameId = computed(() => route.params.id)

    function getGameName() {
      if (!game.value) return ''
      if (game.value.title) return game.value.title
      if (game.value.gameName) return game.value.gameName
      if (game.value.data?.attributes?.displayName) return game.value.data.attributes.displayName
      return 'Unknown'
    }

    function getProvider() {
      if (!game.value) return ''
      if (game.value.studio) return game.value.studio
      if (game.value.providerName) return game.value.providerName
      if (game.value.data?.attributes?.provider?.label) return game.value.data.attributes.provider.label
      return 'Unknown'
    }

    function getCategory() {
      if (!game.value) return ''
      if (game.value.type) return capitalizeWord(game.value.type)
      if (game.value.gameCategory) {
        const categoryMap = { 'LV': 'Live', 'SL': 'Slots', 'TB': 'Table', 'IN': 'Instant', 'JP': 'Jackpot' }
        return categoryMap[game.value.gameCategory] || game.value.gameCategory
      }
      if (game.value.data?.attributes?.classification?.category) return capitalizeWord(game.value.data.attributes.classification.category)
      return 'Unknown'
    }

    function getRtp() {
      if (!game.value) return '0.00'
      if (typeof game.value.returnToPlayer === 'number') return game.value.returnToPlayer.toFixed(2)
      if (game.value.rtpValue) return parseFloat(game.value.rtpValue).toFixed(2)
      if (game.value.data?.attributes?.metrics?.rtp) return (game.value.data.attributes.metrics.rtp * 100).toFixed(2)
      return '0.00'
    }

    function getVolatility() {
      if (!game.value) return 'Unknown'
      if (game.value.variance) return capitalizeWord(game.value.variance)
      if (game.value.riskLevel) {
        const volatilityMap = { 'LOW': 'Low', 'MED': 'Medium', 'HIGH': 'High' }
        return volatilityMap[game.value.riskLevel] || game.value.riskLevel
      }
      if (game.value.data?.attributes?.classification?.volatility) return capitalizeWord(game.value.data.attributes.classification.volatility)
      return 'Unknown'
    }

    function getVolatilityClass() {
      const vol = getVolatility().toLowerCase()
      if (vol.includes('low')) return 'low'
      if (vol.includes('medium') || vol.includes('med')) return 'medium'
      if (vol.includes('high')) return 'high'
      return ''
    }

    function isEnabled() {
      if (!game.value) return false
      if (typeof game.value.active === 'boolean') return game.value.active
      if (game.value.isEnabled !== undefined) return game.value.isEnabled === 1 || game.value.isEnabled === true
      if (game.value.data?.attributes?.status?.enabled !== undefined) return game.value.data.attributes.status.enabled
      return true
    }

    function getFormattedDate() {
      if (!game.value) return 'N/A'
      let date = null
      if (game.value.launchDate) date = new Date(game.value.launchDate)
      else if (game.value.releaseDate) {
        const parts = game.value.releaseDate.split('/')
        if (parts.length === 3) date = new Date(parts[2], parts[1] - 1, parts[0])
      }
      else if (game.value.data?.attributes?.status?.released) date = new Date(game.value.data.attributes.status.released)
      
      if (date && !isNaN(date)) {
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
      }
      return 'N/A'
    }

    function getFeatures() {
      if (!game.value) return []
      if (Array.isArray(game.value.features)) return game.value.features
      if (game.value.tagList) return game.value.tagList.split(',').map(t => t.trim())
      if (Array.isArray(game.value.data?.attributes?.tags)) return game.value.data.attributes.tags.map(t => t.slug || t.name)
      return []
    }

    function formatFeature(feature) {
      return feature.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
    }

    function capitalizeWord(word) {
      if (!word) return ''
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    }

    function getGameThumb() {
      if (!game.value) return ''
      const thumb = game.value.thumbnail || game.value.imageUrl || game.value.data?.attributes?.media?.thumbnailUrl
      if (thumb) return thumb
      return `https://via.placeholder.com/500x300?text=${encodeURIComponent(getGameName())}`
    }

    function onImageError(event) {
      event.target.src = 'https://via.placeholder.com/500x300?text=Game'
    }

    async function loadGame() {
      loading.value = true
      error.value = null
      try {
        const data = await gameService.getGame(gameId.value)
        game.value = data
      } catch (err) {
        error.value = `Could not load game: ${err.message || 'Game not found'}`
        console.error('Error loading game:', err)
      } finally {
        loading.value = false
      }
    }

    function goBack() {
      window.history.back()
    }

    onMounted(() => {
      loadGame()
    })

    return {
      game, gameId, loading, error, getGameName, getProvider, getCategory, getRtp, getVolatility,
      getVolatilityClass, isEnabled, getFormattedDate, getFeatures, formatFeature, getGameThumb,
      onImageError, goBack
    }
  }
}
</script>

<style scoped>
.game-detail-view { padding: 2rem 0; }
.btn-back { display: inline-flex; align-items: center; padding: 0.75rem 1.5rem; background: rgba(255, 255, 255, 0.9); color: var(--primary); border: 2px solid var(--primary); border-radius: 0.5rem; cursor: pointer; font-weight: 600; font-size: 1rem; transition: all 0.3s ease; margin-bottom: 2rem; }
.btn-back:hover { background: var(--primary); color: white; }
.loading-state { display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 1rem; padding: 4rem 2rem; background: white; border-radius: 1rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
.spinner { width: 40px; height: 40px; border: 4px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.error-state { padding: 4rem 2rem; background: white; border-radius: 1rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); text-align: center; }
.error-state h2 { color: var(--danger); margin-bottom: 1rem; }
.error-state p { color: var(--text-light); margin-bottom: 2rem; font-size: 1.125rem; }
.btn-home { display: inline-block; padding: 0.75rem 2rem; background: var(--primary); color: white; border-radius: 0.5rem; font-weight: 600; transition: all 0.3s ease; }
.btn-home:hover { background: var(--primary-dark); }
.game-detail { background: white; border-radius: 1rem; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.detail-header { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; padding: 3rem; }
.detail-image { position: relative; height: 400px; border-radius: 0.75rem; overflow: hidden; background: var(--light); }
.detail-image img { width: 100%; height: 100%; object-fit: cover; }
.detail-info { display: flex; flex-direction: column; }
.game-name { font-size: 2.5rem; font-weight: 700; margin-bottom: 2rem; color: var(--text); }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem; }
.info-item { display: flex; flex-direction: column; }
.info-item label { font-weight: 600; font-size: 0.875rem; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
.info-value { font-size: 1.25rem; font-weight: 600; color: var(--text); }
.info-value.rtp { color: var(--success); }
.info-value.volatility { display: inline-block; padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 1rem; font-weight: 600; }
.info-value.volatility.low { background: #d1fae5; color: #065f46; }
.info-value.volatility.medium { background: #fef3c7; color: #92400e; }
.info-value.volatility.high { background: #fee2e2; color: #991b1b; }
.info-value.enabled { color: var(--success); }
.info-value.disabled { color: var(--danger); }
.features-section { margin-bottom: 2rem; }
.features-section label { font-weight: 600; font-size: 0.875rem; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; display: block; }
.features-list { display: flex; flex-wrap: wrap; gap: 0.75rem; }
.feature-tag { display: inline-block; padding: 0.5rem 1rem; background: var(--light); color: var(--primary); border-radius: 2rem; font-size: 0.875rem; font-weight: 600; }
.actions { margin-top: auto; }
.btn-launch { width: 100%; padding: 1.25rem; background: var(--primary); color: white; border: none; border-radius: 0.75rem; font-size: 1.125rem; font-weight: 700; cursor: pointer; transition: all 0.3s ease; }
.btn-launch:hover:not(.disabled) { background: var(--primary-dark); transform: translateY(-2px); box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3); }
.btn-launch.disabled { background: var(--border); cursor: not-allowed; color: var(--text-light); }
.stats-section { padding: 3rem; background: var(--light); }
.stats-section h2 { margin-bottom: 2rem; color: var(--text); }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }
.stat-card { background: white; padding: 1.5rem; border-radius: 0.75rem; text-align: center; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); }
.stat-card h3 { font-size: 0.875rem; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem; font-weight: 600; }
.stat-value { font-size: 1.5rem; font-weight: 700; color: var(--primary); }
@media (max-width: 1024px) { .detail-header { grid-template-columns: 1fr; } .info-grid { grid-template-columns: 1fr; } .stats-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .game-name { font-size: 1.75rem; } .detail-header { padding: 1.5rem; } .detail-image { height: 250px; } .stats-grid { grid-template-columns: 1fr; } }
</style>
