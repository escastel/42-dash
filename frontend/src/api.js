const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3000'

export const gameService = {
  async listGames(params = {}) {
    const query = new URLSearchParams()
    
    if (params.search) query.append('search', params.search)
    if (params.provider) query.append('provider', params.provider)
    if (params.category) query.append('category', params.category)
    if (params.enabled !== undefined) query.append('enabled', params.enabled)
    if (params.sort) query.append('sort', params.sort)
    if (params.order) query.append('order', params.order)
    if (params.page) query.append('page', params.page)
    if (params.pageSize) query.append('pageSize', params.pageSize)

    const response = await fetch(`${API_BASE}/api/games?${query}`)
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    return response.json()
  },

  async getGame(id) {
    const response = await fetch(`${API_BASE}/api/games/${id}`)
    if (!response.ok) {
      throw new Error(`Game not found: ${response.status}`)
    }
    return response.json()
  },

  async launchGame(gameId, mode) {
    const response = await fetch(`${API_BASE}/api/launch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gameId, mode }),
    })
    if (!response.ok) {
      throw new Error(`Launch failed: ${response.status}`)
    }
    return response.json()
  },
}

export const walletService = {
  async getBalance() {
    const response = await fetch(`${API_BASE}/api/wallet/balance`)
    if (!response.ok) {
      throw new Error(`Wallet error: ${response.status}`)
    }
    return response.json()
  },
}
