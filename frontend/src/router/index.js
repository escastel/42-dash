import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import GameDetailView from '../views/GameDetailView.vue'
import WalletView from '../views/WalletView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
  },
  {
    path: '/games/:id',
    name: 'GameDetail',
    component: GameDetailView,
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: WalletView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
