<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import apiService from '@/services/api'
import type { Survey } from '@/types/survey'

const surveys = ref<Survey[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const searchQuery = ref('')

const filteredSurveys = computed(() => {
  if (!searchQuery.value) return surveys.value
  const query = searchQuery.value.toLowerCase()
  return surveys.value.filter(
    survey =>
      survey.title.toLowerCase().includes(query) ||
      survey.description?.toLowerCase().includes(query)
  )
})

const fetchSurveys = async () => {
  try {
    loading.value = true
    error.value = null
    surveys.value = await apiService.getAllSurveys()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Nie udało się pobrać ankiet'
    console.error('Error fetching surveys:', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('Skopiowano do schowka!')
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

onMounted(() => {
  fetchSurveys()
})
</script>

<template>
  <div class="surveys-list-view">
    <div class="page-header">
      <div class="header-content">
        <h1>📋 Lista ankiet</h1>
        <p>Przeglądaj i zarządzaj swoimi ankietami</p>
      </div>
      <RouterLink to="/surveys/create" class="btn btn-primary">
        ➕ Nowa ankieta
      </RouterLink>
    </div>

    <div class="search-bar">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="🔍 Szukaj ankiet..."
        class="search-input"
      />
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Ładowanie ankiet...</p>
    </div>

    <div v-else-if="error" class="error">
      <div class="error-icon">⚠️</div>
      <h3>Błąd</h3>
      <p>{{ error }}</p>
      <button @click="fetchSurveys" class="btn btn-secondary">
        🔄 Spróbuj ponownie
      </button>
    </div>

    <div v-else-if="surveys.length === 0" class="empty-state">
      <div class="empty-icon">📭</div>
      <h3>Brak ankiet</h3>
      <p>Nie masz jeszcze żadnych ankiet. Utwórz pierwszą!</p>
      <RouterLink to="/surveys/create" class="btn btn-primary">
        ➕ Utwórz ankietę
      </RouterLink>
    </div>

    <div v-else class="surveys-grid">
      <div
        v-for="survey in filteredSurveys"
        :key="survey.id"
        class="survey-card"
      >
        <div class="survey-header">
          <h3>{{ survey.title }}</h3>
          <span class="question-count">
            {{ survey.questions.length }} pytań
          </span>
        </div>

        <p v-if="survey.description" class="survey-description">
          {{ survey.description }}
        </p>

        <div class="survey-meta">
          <span class="created-at">
            🗓️ {{ formatDate(survey.created_at) }}
          </span>
        </div>

        <div class="survey-actions">
          <RouterLink :to="`/surveys/${survey.id}`" class="btn btn-action btn-fill">
            ✏️ Wypełnij
          </RouterLink>
          <RouterLink :to="`/surveys/${survey.id}/stats`" class="btn btn-action btn-stats">
            📊 Statystyki
          </RouterLink>
          <button
            @click="copyToClipboard(survey.links.survey_url)"
            class="btn btn-action btn-copy"
            title="Kopiuj link"
          >
            📋
          </button>
        </div>
      </div>
    </div>

    <div v-if="filteredSurveys.length === 0 && surveys.length > 0" class="no-results">
      <p>Nie znaleziono ankiet pasujących do "{{ searchQuery }}"</p>
    </div>
  </div>
</template>

<style scoped>
.surveys-list-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-content h1 {
  margin: 0;
  color: #333;
  font-size: 2rem;
}

.header-content p {
  margin: 0.5rem 0 0;
  color: #666;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
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

.search-bar {
  margin-bottom: 2rem;
}

.search-input {
  width: 100%;
  padding: 1rem 1.5rem;
  font-size: 1.1rem;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.loading {
  text-align: center;
  padding: 4rem;
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

.error,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.error-icon,
.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error {
  color: #d32f2f;
}

.surveys-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.survey-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
}

.survey-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.survey-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.survey-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.3rem;
  flex: 1;
}

.question-count {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.survey-description {
  color: #666;
  margin: 0 0 1rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.survey-meta {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.created-at {
  color: #888;
  font-size: 0.9rem;
}

.survey-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-action {
  flex: 1;
  min-width: 100px;
  padding: 0.6rem 1rem;
  font-size: 0.9rem;
  justify-content: center;
}

.btn-fill {
  background: #667eea;
  color: white;
}

.btn-fill:hover {
  background: #5568d3;
}

.btn-stats {
  background: #f0f4ff;
  color: #667eea;
}

.btn-stats:hover {
  background: #667eea;
  color: white;
}

.btn-copy {
  flex: 0;
  min-width: auto;
  background: #f5f5f5;
  color: #666;
}

.btn-copy:hover {
  background: #667eea;
  color: white;
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #666;
  background: white;
  border-radius: 12px;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .surveys-grid {
    grid-template-columns: 1fr;
  }

  .survey-actions {
    flex-direction: column;
  }

  .btn-action {
    width: 100%;
  }
}
</style>
