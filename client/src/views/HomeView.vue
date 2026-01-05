<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import apiService from '@/services/api'
import type { HealthStatus, ApiInfo } from '@/types/survey'

const healthStatus = ref<HealthStatus | null>(null)
const apiInfo = ref<ApiInfo | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const fetchHealthStatus = async () => {
  try {
    loading.value = true
    error.value = null
    
    const [health, info] = await Promise.all([
      apiService.getHealth(),
      apiService.getApiInfo()
    ])
    
    healthStatus.value = health
    apiInfo.value = info
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unknown error occurred'
    console.error('Error fetching health status:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchHealthStatus()
})
</script>

<template>
  <div class="home-view">
    <div class="hero">
      <h1>🗳️ Polly</h1>
      <p class="subtitle">Twórz i zarządzaj ankietami w prosty sposób</p>
      
      <div class="hero-buttons">
        <RouterLink to="/surveys/create" class="btn btn-primary">
          ➕ Utwórz ankietę
        </RouterLink>
        <RouterLink to="/surveys" class="btn btn-secondary">
          📋 Przeglądaj ankiety
        </RouterLink>
      </div>
    </div>

    <div class="health-card">
      <div class="card-header">
        <h2>Status backendu</h2>
        <button @click="fetchHealthStatus" class="refresh-btn" :disabled="loading">
          {{ loading ? '⟳' : '🔄' }} Odśwież
        </button>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Sprawdzanie statusu...</p>
      </div>

      <div v-else-if="error" class="error">
        <div class="error-icon">⚠️</div>
        <h3>Błąd połączenia</h3>
        <p>{{ error }}</p>
        <p class="error-hint">Upewnij się, że backend działa pod adresem: <code>{{ API_URL }}</code></p>
      </div>

      <div v-else-if="healthStatus && apiInfo" class="status-content">
        <div class="status-indicator" :class="healthStatus.status">
          <span class="status-dot"></span>
          <span class="status-text">{{ healthStatus.status.toUpperCase() }}</span>
        </div>

        <div class="info-grid">
          <div class="info-card">
            <h3>Informacje o API</h3>
            <div class="info-item">
              <span class="label">Nazwa:</span>
              <span class="value">{{ apiInfo.name }}</span>
            </div>
            <div class="info-item">
              <span class="label">Wersja:</span>
              <span class="value">{{ apiInfo.version }}</span>
            </div>
            <div class="info-item">
              <span class="label">Dokumentacja:</span>
              <a :href="`${API_URL}${apiInfo.docs}`" target="_blank" class="link">
                Swagger UI
              </a>
            </div>
          </div>

          <div class="info-card">
            <h3>Statystyki bazy</h3>
            <div class="stat-item">
              <span class="stat-label">📊 Ankiety</span>
              <span class="stat-value">{{ healthStatus.database.surveys }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">💬 Odpowiedzi</span>
              <span class="stat-value">{{ healthStatus.database.responses }}</span>
            </div>
          </div>
        </div>

        <div class="connection-info">
          <p><strong>Połączono z:</strong> <code>{{ API_URL }}</code></p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 4rem;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.4rem;
  color: #666;
  margin-top: 0.5rem;
  margin-bottom: 2rem;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
}

.health-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.card-header h2 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

.refresh-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 1rem;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 2rem;
  color: #d32f2f;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error h3 {
  margin: 0.5rem 0;
}

.error-hint {
  margin-top: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.error code {
  background: #f5f5f5;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}

.status-content {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 2rem;
  font-weight: 600;
  font-size: 1.2rem;
}

.status-indicator.healthy {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s ease infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.info-card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
}

.info-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e0e0e0;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  font-weight: 500;
  color: #666;
}

.value {
  color: #333;
  font-weight: 600;
}

.link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.link:hover {
  text-decoration: underline;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 8px;
  margin-bottom: 0.75rem;
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-label {
  font-weight: 500;
  color: #666;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
}

.connection-info {
  background: #f0f4ff;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  color: #333;
}

.connection-info code {
  background: white;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  color: #667eea;
  font-weight: 600;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2.5rem;
  }

  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
