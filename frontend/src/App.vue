<template>
  <div id="app" class="app">
    <header class="header">
      <div class="container header-content">
        <router-link to="/" class="logo">
          <h1>⚡ QTech Dash</h1>
        </router-link>
        <nav class="nav">
          <router-link to="/" class="nav-link">Catalog</router-link>
          <router-link to="/wallet" class="nav-link">Wallet</router-link>
        </nav>
      </div>
    </header>

    <main class="main">
      <router-view />
    </main>

    <footer class="footer">
      <div class="container">
        <p>&copy; 2026 QTech Games. Game Aggregator Arena.</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  padding: 1.5rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  text-decoration: none;
  color: var(--primary);
}

.logo h1 {
  font-size: 1.5rem;
  margin: 0;
}

.logo:hover h1 {
  color: var(--secondary);
}

.nav {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: var(--text-primary);
  font-weight: 500;
  transition: color 0.2s;
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.main {
  flex: 1;
  padding: 2rem 0;
}

.footer {
  background-color: var(--bg-secondary);
  border-top: 1px solid var(--border);
  padding: 2rem 0;
  text-align: center;
  color: var(--text-secondary);
  margin-top: 4rem;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }

  .nav {
    gap: 1rem;
  }

  .logo h1 {
    font-size: 1.25rem;
  }
}
</style>
