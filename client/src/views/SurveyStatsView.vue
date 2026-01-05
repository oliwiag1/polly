<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import apiService from '@/services/api'
import { QuestionType, type SurveyStats, type QuestionStats } from '@/types/survey'

const route = useRoute()

const stats = ref<SurveyStats | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const surveyId = computed(() => route.params.id as string)

const fetchStats = async () => {
  try {
    loading.value = true
    error.value = null
    stats.value = await apiService.getSurveyStats(surveyId.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Nie udało się pobrać statystyk'
    console.error('Error fetching stats:', err)
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

const getQuestionTypeIcon = (type: QuestionType): string => {
  const icons: Record<QuestionType, string> = {
    [QuestionType.TEXT]: '📝',
    [QuestionType.SINGLE_CHOICE]: '⭕',
    [QuestionType.MULTIPLE_CHOICE]: '☑️',
    [QuestionType.RATING]: '⭐',
    [QuestionType.YES_NO]: '✅'
  }
  return icons[type]
}

const getMaxDistributionValue = (question: QuestionStats): number => {
  const values = Object.values(question.answer_distribution)
  return Math.max(...values, 1)
}

const getDistributionPercentage = (count: number, max: number): number => {
  return (count / max) * 100
}

const getSurveyLink = () => {
  return `${window.location.origin}/surveys/${surveyId.value}`
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
  fetchStats()
})
</script>

<template>
  <div class="survey-stats-view">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Ładowanie statystyk...</p>
    </div>

    <div v-else-if="error" class="error">
      <div class="error-icon">⚠️</div>
      <h3>Błąd</h3>
      <p>{{ error }}</p>
      <RouterLink to="/surveys" class="btn btn-secondary">
        ← Wróć do listy
      </RouterLink>
    </div>

    <template v-else-if="stats">
      <div class="page-header">
        <div class="header-content">
          <h1>📊 {{ stats.survey_title }}</h1>
          <p>Statystyki ankiety</p>
        </div>
        <div class="header-actions">
          <button @click="fetchStats" class="btn btn-refresh" :disabled="loading">
            🔄 Odśwież
          </button>
          <RouterLink :to="`/surveys/${surveyId}`" class="btn btn-secondary">
            ✏️ Wypełnij ankietę
          </RouterLink>
        </div>
      </div>

      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-icon">💬</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total_responses }}</span>
            <span class="stat-label">Odpowiedzi</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">❓</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.questions_stats.length }}</span>
            <span class="stat-label">Pytań</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🗓️</div>
          <div class="stat-info">
            <span class="stat-value-small">{{ formatDate(stats.created_at) }}</span>
            <span class="stat-label">Data utworzenia</span>
          </div>
        </div>
        <div class="stat-card" v-if="stats.last_response_at">
          <div class="stat-icon">⏰</div>
          <div class="stat-info">
            <span class="stat-value-small">{{ formatDate(stats.last_response_at) }}</span>
            <span class="stat-label">Ostatnia odpowiedź</span>
          </div>
        </div>
      </div>

      <div class="share-section">
        <h2>🔗 Udostępnij ankietę</h2>
        <div class="share-link">
          <input type="text" :value="getSurveyLink()" readonly />
          <button @click="copyToClipboard(getSurveyLink())" class="btn btn-copy">
            📋 Kopiuj
          </button>
        </div>
      </div>

      <div class="questions-stats">
        <h2>📈 Statystyki pytań</h2>

        <div v-if="stats.total_responses === 0" class="no-responses">
          <div class="no-responses-icon">📭</div>
          <h3>Brak odpowiedzi</h3>
          <p>Nikt jeszcze nie wypełnił tej ankiety. Udostępnij link!</p>
        </div>

        <div v-else class="questions-list">
          <div
            v-for="(question, index) in stats.questions_stats"
            :key="question.question_id"
            class="question-stats-card"
          >
            <div class="question-header">
              <span class="question-number">{{ index + 1 }}</span>
              <div class="question-info">
                <h3>
                  {{ getQuestionTypeIcon(question.question_type) }}
                  {{ question.question_text }}
                </h3>
                <p class="question-responses">
                  {{ question.total_responses }} odpowiedzi
                </p>
              </div>
            </div>

            <div class="question-distribution">
              <!-- Dla pytań z rozkładem -->
              <template v-if="Object.keys(question.answer_distribution).length > 0">
                <div
                  v-for="(count, answer) in question.answer_distribution"
                  :key="answer"
                  class="distribution-item"
                >
                  <div class="distribution-label">
                    <span class="answer-text">{{ answer }}</span>
                    <span class="answer-count">{{ count }}</span>
                  </div>
                  <div class="distribution-bar">
                    <div
                      class="distribution-fill"
                      :style="{
                        width: getDistributionPercentage(count, getMaxDistributionValue(question)) + '%'
                      }"
                    ></div>
                  </div>
                </div>
              </template>

              <!-- Dla pytań z średnią (rating) -->
              <div v-if="question.average_value !== null && question.average_value !== undefined" class="average-section">
                <div class="average-label">Średnia ocena:</div>
                <div class="average-value">
                  <span class="average-number">{{ question.average_value.toFixed(2) }}</span>
                  <span class="average-stars">
                    <span v-for="n in 5" :key="n" class="star" :class="{ active: n <= Math.round(question.average_value!) }">
                      ⭐
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="actions-footer">
        <RouterLink to="/surveys" class="btn btn-secondary">
          ← Wróć do listy
        </RouterLink>
      </div>
    </template>
  </div>
</template>

<style scoped>
.survey-stats-view {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
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

.error {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  color: #d32f2f;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
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

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
}

.btn-refresh {
  background: #e8f5e9;
  color: #2e7d32;
  border: 2px solid #2e7d32;
}

.btn-refresh:hover:not(:disabled) {
  background: #2e7d32;
  color: white;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-copy {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-copy:hover {
  transform: translateY(-2px);
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #667eea;
}

.stat-value-small {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.share-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
}

.share-section h2 {
  margin: 0 0 1rem;
  color: #333;
  font-size: 1.3rem;
}

.share-link {
  display: flex;
  gap: 0.75rem;
}

.share-link input {
  flex: 1;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  background: #f8f9fa;
  color: #666;
}

.questions-stats {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
}

.questions-stats h2 {
  margin: 0 0 1.5rem;
  color: #333;
  font-size: 1.3rem;
}

.no-responses {
  text-align: center;
  padding: 3rem;
  background: #f8f9fa;
  border-radius: 12px;
}

.no-responses-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.no-responses h3 {
  margin: 0 0 0.5rem;
  color: #333;
}

.no-responses p {
  color: #666;
  margin: 0;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.question-stats-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
}

.question-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.question-number {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.question-info h3 {
  margin: 0;
  color: #333;
  font-size: 1.1rem;
}

.question-responses {
  margin: 0.3rem 0 0;
  color: #888;
  font-size: 0.9rem;
}

.question-distribution {
  padding-left: 3rem;
}

.distribution-item {
  margin-bottom: 1rem;
}

.distribution-item:last-child {
  margin-bottom: 0;
}

.distribution-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.3rem;
}

.answer-text {
  color: #333;
  font-weight: 500;
}

.answer-count {
  color: #667eea;
  font-weight: 700;
}

.distribution-bar {
  height: 24px;
  background: #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
}

.distribution-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  transition: width 0.5s ease;
  min-width: 2px;
}

.average-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 10px;
  margin-top: 1rem;
}

.average-label {
  color: #666;
  font-weight: 500;
}

.average-value {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.average-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
}

.average-stars .star {
  font-size: 1.2rem;
  filter: grayscale(100%);
  opacity: 0.3;
}

.average-stars .star.active {
  filter: grayscale(0%);
  opacity: 1;
}

.actions-footer {
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
    justify-content: center;
  }

  .share-link {
    flex-direction: column;
  }

  .question-distribution {
    padding-left: 0;
  }

  .average-section {
    flex-direction: column;
    text-align: center;
  }
}
</style>
