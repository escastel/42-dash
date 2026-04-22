<template>
  <div class="wallet-view">
    <div class="container">
      <h1>Wallet Dashboard</h1>

      <div class="balance-card">
        <h2>Current Balance</h2>
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
        </div>
        <div v-else class="balance-display" data-testid="wallet-balance">
          <p class="balance-amount">{{ formatCurrency(balance) }}</p>
          <button @click="loadBalance" class="btn-refresh">↻ Refresh</button>
        </div>
      </div>

      <div class="empty-state">
        <p>Full wallet feature coming in Level 2</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { walletService } from '../api.js'

export default {
  name: 'WalletView',
  setup() {
    const balance = ref(0)
    const loading = ref(false)

    function formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
    }

    async function loadBalance() {
      loading.value = true
      try {
        const response = await walletService.getBalance()
        balance.value = response.balance || 0
      } catch (err) {
        console.error('Error loading balance:', err)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadBalance()
    })

    return { balance, loading, formatCurrency, loadBalance }
  }
}
</script>

<style scoped>
.wallet-view {
  padding: 2rem 0;
}

.balance-card {
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: white;
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3);
  margin-bottom: 2rem;
}

.balance-card h2 {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.95;
}

.balance-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.balance-amount {
  font-size: 3rem;
  font-weight: 700;
  letter-spacing: -0.05em;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-refresh {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-refresh:hover {
  background: rgba(255, 255, 255, 0.3);
}

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  color: var(--text-secondary);
}

@media (max-width: 640px) {
  .balance-display {
    flex-direction: column;
    text-align: center;
  }

  .balance-amount {
    font-size: 2.5rem;
  }
}
</style>
