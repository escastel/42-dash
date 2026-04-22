<template>
  <div class="game-card" data-testid="game-card" @click="$emit('click')">
    <div class="card-image">
      <img
        :src="thumbnailUrl"
        :alt="gameName"
        @error="onImageError"
      />
      <div class="card-overlay">
        <span v-if="!game.enabled" class="badge-disabled">Disabled</span>
      </div>
    </div>

    <div class="card-content">
      <h3 class="game-name">{{ gameName }}</h3>
      <p class="game-provider">{{ providerName }}</p>

      <div class="card-meta">
        <span class="meta-item">
          <span class="label">RTP</span>
          <span class="value">{{ rtp }}%</span>
        </span>
        <span class="meta-item">
          <span class="label">Category</span>
          <span class="value">{{ categoryLabel }}</span>
        </span>
      </div>

      <div class="card-footer">
        <button class="btn-view" @click.stop="$emit('click')">View</button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'GameCard',
  props: {
    game: {
      type: Object,
      required: true,
    },
  },
  emits: ['click'],
  setup(props) {
    const gameName = computed(() => {
      const game = props.game
      if (game.name) return game.name
      if (game.title) return game.title
      if (game.gameName) return game.gameName
      return 'Unknown'
    })

    const providerName = computed(() => {
      const game = props.game
      if (game.provider) return game.provider
      if (game.studio) return game.studio
      if (game.providerName) return game.providerName
      return 'Unknown'
    })

    const categoryLabel = computed(() => {
      const game = props.game
      const category = game.category || game.type || ''
      return category.charAt(0).toUpperCase() + category.slice(1).toLowerCase()
    })

    const rtp = computed(() => {
      const game = props.game
      if (typeof game.rtp === 'number') return game.rtp.toFixed(2)
      return '0.00'
    })

    const thumbnailUrl = computed(() => {
      const game = props.game
      return game.thumbnailUrl || 'https://via.placeholder.com/300x200?text=Game'
    })

    function onImageError(e) {
      e.target.src = 'https://via.placeholder.com/300x200?text=Game'
    }

    return {
      gameName,
      providerName,
      categoryLabel,
      rtp,
      thumbnailUrl,
      onImageError,
    }
  },
}
</script>

<style scoped>
.game-card {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.game-card:hover {
  border-color: var(--primary);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(99, 102, 241, 0.2);
}

.card-image {
  position: relative;
  width: 100%;
  padding-bottom: 66.67%;
  overflow: hidden;
  background-color: rgba(0, 0, 0, 0.2);
}

.card-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.game-card:hover .card-image img {
  transform: scale(1.05);
}

.card-overlay {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  transition: background 0.3s;
}

.game-card:hover .card-overlay {
  background: rgba(0, 0, 0, 0.5);
}

.badge-disabled {
  background-color: var(--danger);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.card-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.game-name {
  font-size: 1.125rem;
  margin-bottom: 0.25rem;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.game-provider {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
}

.card-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-grow: 1;
}

.meta-item {
  display: flex;
  flex-direction: column;
  font-size: 0.75rem;
}

.meta-item .label {
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

.meta-item .value {
  color: var(--primary);
  font-weight: 600;
  font-size: 1rem;
}

.card-footer {
  display: flex;
  gap: 0.5rem;
}

.btn-view {
  flex: 1;
  padding: 0.625rem;
  font-size: 0.875rem;
  background-color: var(--primary);
  color: white;
}

.btn-view:hover {
  background-color: var(--secondary);
}

@media (max-width: 480px) {
  .card-content {
    padding: 0.75rem;
  }

  .game-name {
    font-size: 1rem;
  }
}
</style>
