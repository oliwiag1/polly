<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <nav class="main-nav">
      <div class="nav-brand">
        <RouterLink to="/" class="brand-link">
          🗳️ Polly
        </RouterLink>
      </div>
      <div class="nav-links">
        <RouterLink to="/" class="nav-link">
          🏠 Strona główna
        </RouterLink>
        <RouterLink to="/surveys" class="nav-link">
          📋 Ankiety
        </RouterLink>
        <RouterLink to="/surveys/create" class="nav-link nav-link-primary">
          ➕ Nowa ankieta
        </RouterLink>
      </div>
    </nav>

    <main class="main-content">
      <RouterView />
    </main>

    <footer class="main-footer">
      <p>Polly Survey Application © 2025</p>
    </footer>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.main-nav {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand {
  display: flex;
  align-items: center;
}

.brand-link {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  text-decoration: none;
  transition: color 0.3s ease;
}

.brand-link:hover {
  color: #667eea;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.nav-link {
  padding: 0.6rem 1rem;
  border-radius: 8px;
  text-decoration: none;
  color: #666;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background: #f0f4ff;
  color: #667eea;
}

.nav-link.router-link-active {
  background: #f0f4ff;
  color: #667eea;
}

.nav-link-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
}

.nav-link-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.nav-link-primary.router-link-active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.main-content {
  flex: 1;
}

.main-footer {
  text-align: center;
  padding: 1.5rem;
  color: #888;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.main-footer p {
  margin: 0;
}

@media (max-width: 768px) {
  .main-nav {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }

  .nav-link {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
  }
}
</style>