<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiService from '@/services/api'
import { QuestionType, type Survey, type Answer, type AnswerSubmit } from '@/types/survey'

const route = useRoute()
const router = useRouter()

const survey = ref<Survey | null>(null)
const answers = ref<Record<string, Answer['value']>>({})
const loading = ref(true)
const submitting = ref(false)
const error = ref<string | null>(null)

const surveyId = computed(() => route.params.id as string)

const fetchSurvey = async () => {
  try {
    loading.value = true
    error.value = null
    survey.value = await apiService.getSurvey(surveyId.value)
    
    // Inicjalizacja odpowiedzi
    survey.value.questions.forEach(q => {
      if (q.type === QuestionType.MULTIPLE_CHOICE) {
        answers.value[q.id] = []
      } else if (q.type === QuestionType.YES_NO) {
        answers.value[q.id] = ''
      } else if (q.type === QuestionType.RATING) {
        answers.value[q.id] = 0
      } else {
        answers.value[q.id] = ''
      }
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Nie udało się pobrać ankiety'
    console.error('Error fetching survey:', err)
  } finally {
    loading.value = false
  }
}

const isValid = computed(() => {
  if (!survey.value) return false
  
  return survey.value.questions.every(q => {
    if (!q.required) return true
    
    const answer = answers.value[q.id]
    if (Array.isArray(answer)) {
      return answer.length > 0
    }
    if (typeof answer === 'number') {
      return answer > 0
    }
    return answer !== '' && answer !== null && answer !== undefined
  })
})

const getQuestionTypeLabel = (type: QuestionType): string => {
  const labels: Record<QuestionType, string> = {
    [QuestionType.TEXT]: 'Odpowiedź tekstowa',
    [QuestionType.SINGLE_CHOICE]: 'Wybierz jedną opcję',
    [QuestionType.MULTIPLE_CHOICE]: 'Wybierz wiele opcji',
    [QuestionType.RATING]: 'Oceń',
    [QuestionType.YES_NO]: 'Tak lub Nie'
  }
  return labels[type]
}

const toggleMultipleChoice = (questionId: string, option: string) => {
  const current = answers.value[questionId] as string[]
  const index = current.indexOf(option)
  if (index > -1) {
    current.splice(index, 1)
  } else {
    current.push(option)
  }
}

const setRating = (questionId: string, value: number) => {
  answers.value[questionId] = value
}

const submitSurvey = async () => {
  if (!isValid.value || !survey.value) return

  try {
    submitting.value = true
    error.value = null

    const answerData: AnswerSubmit = {
      answers: Object.entries(answers.value).map(([question_id, value]) => ({
        question_id,
        value
      }))
    }

    await apiService.submitResponse(surveyId.value, answerData)
    router.push(`/surveys/${surveyId.value}/success`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Nie udało się wysłać odpowiedzi'
    console.error('Error submitting response:', err)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchSurvey()
})
</script>

<template>
  <div class="fill-survey-view">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Ładowanie ankiety...</p>
    </div>

    <div v-else-if="error" class="error">
      <div class="error-icon">⚠️</div>
      <h3>Błąd</h3>
      <p>{{ error }}</p>
      <router-link to="/surveys" class="btn btn-secondary">
        ← Wróć do listy
      </router-link>
    </div>

    <template v-else-if="survey">
      <div class="survey-header">
        <h1>{{ survey.title }}</h1>
        <p v-if="survey.description" class="survey-description">
          {{ survey.description }}
        </p>
        <div class="survey-meta">
          <span>📋 {{ survey.questions.length }} pytań</span>
        </div>
      </div>

      <form @submit.prevent="submitSurvey" class="survey-form">
        <div
          v-for="(question, index) in survey.questions"
          :key="question.id"
          class="question-card"
        >
          <div class="question-header">
            <span class="question-number">{{ index + 1 }}</span>
            <div class="question-content">
              <h3>
                {{ question.text }}
                <span v-if="question.required" class="required-mark">*</span>
              </h3>
              <p class="question-hint">{{ getQuestionTypeLabel(question.type) }}</p>
            </div>
          </div>

          <!-- Tekst -->
          <div v-if="question.type === QuestionType.TEXT" class="answer-section">
            <textarea
              v-model="answers[question.id] as string"
              placeholder="Wpisz swoją odpowiedź..."
              rows="3"
              :required="question.required"
            ></textarea>
          </div>

          <!-- Jednokrotny wybór -->
          <div v-else-if="question.type === QuestionType.SINGLE_CHOICE" class="answer-section">
            <div class="options-list">
              <label
                v-for="option in question.options"
                :key="option"
                class="option-item radio"
                :class="{ selected: answers[question.id] === option }"
              >
                <input
                  type="radio"
                  :name="question.id"
                  :value="option"
                  v-model="answers[question.id]"
                  :required="question.required"
                />
                <span class="option-marker">○</span>
                <span class="option-text">{{ option }}</span>
              </label>
            </div>
          </div>

          <!-- Wielokrotny wybór -->
          <div v-else-if="question.type === QuestionType.MULTIPLE_CHOICE" class="answer-section">
            <div class="options-list">
              <label
                v-for="option in question.options"
                :key="option"
                class="option-item checkbox"
                :class="{ selected: (answers[question.id] as string[]).includes(option) }"
              >
                <input
                  type="checkbox"
                  :value="option"
                  :checked="(answers[question.id] as string[]).includes(option)"
                  @change="toggleMultipleChoice(question.id, option)"
                />
                <span class="option-marker">☐</span>
                <span class="option-text">{{ option }}</span>
              </label>
            </div>
          </div>

          <!-- Ocena -->
          <div v-else-if="question.type === QuestionType.RATING" class="answer-section">
            <div class="rating-input">
              <button
                v-for="n in (question.max_rating || 5) - (question.min_rating || 1) + 1"
                :key="n"
                type="button"
                class="rating-star"
                :class="{ active: (answers[question.id] as number) >= n + (question.min_rating || 1) - 1 }"
                @click="setRating(question.id, n + (question.min_rating || 1) - 1)"
              >
                ⭐
              </button>
            </div>
            <p class="rating-value" v-if="answers[question.id]">
              Wybrano: {{ answers[question.id] }} / {{ question.max_rating || 5 }}
            </p>
          </div>

          <!-- Tak / Nie -->
          <div v-else-if="question.type === QuestionType.YES_NO" class="answer-section">
            <div class="yes-no-buttons">
              <button
                type="button"
                class="yes-no-btn yes"
                :class="{ selected: answers[question.id] === 'yes' }"
                @click="answers[question.id] = 'yes'"
              >
                ✓ Tak
              </button>
              <button
                type="button"
                class="yes-no-btn no"
                :class="{ selected: answers[question.id] === 'no' }"
                @click="answers[question.id] = 'no'"
              >
                ✗ Nie
              </button>
            </div>
          </div>
        </div>

        <div v-if="error" class="error-message">
          ⚠️ {{ error }}
        </div>

        <div class="form-actions">
          <router-link to="/surveys" class="btn btn-secondary">
            ← Anuluj
          </router-link>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="!isValid || submitting"
          >
            {{ submitting ? '⏳ Wysyłanie...' : '📤 Wyślij odpowiedzi' }}
          </button>
        </div>
      </form>
    </template>
  </div>
</template>

<style scoped>
.fill-survey-view {
  padding: 2rem;
  max-width: 800px;
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

.survey-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2.5rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  text-align: center;
}

.survey-header h1 {
  margin: 0 0 0.5rem;
  font-size: 2rem;
}

.survey-description {
  opacity: 0.9;
  margin: 0 0 1rem;
  font-size: 1.1rem;
}

.survey-meta {
  opacity: 0.8;
  font-size: 0.95rem;
}

.survey-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.question-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.question-card:hover {
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.12);
}

.question-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.question-number {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.question-content h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
}

.required-mark {
  color: #d32f2f;
}

.question-hint {
  margin: 0.3rem 0 0;
  color: #888;
  font-size: 0.9rem;
}

.answer-section {
  margin-top: 1rem;
}

.answer-section textarea {
  width: 100%;
  padding: 1rem;
  font-size: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  resize: vertical;
  font-family: inherit;
  transition: all 0.3s ease;
}

.answer-section textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.option-item:hover {
  background: #f0f4ff;
}

.option-item.selected {
  background: #e8f0fe;
  border-color: #667eea;
}

.option-item input {
  display: none;
}

.option-marker {
  font-size: 1.3rem;
  color: #667eea;
}

.option-item.selected .option-marker {
  color: #667eea;
}

.option-item.radio.selected .option-marker::after {
  content: '●';
}

.option-item.checkbox.selected .option-marker::after {
  content: '☑';
}

.option-item.selected .option-marker {
  visibility: hidden;
}

.option-item.selected .option-marker::after {
  visibility: visible;
  position: absolute;
}

.option-text {
  color: #333;
  font-size: 1rem;
}

.rating-input {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.rating-star {
  background: none;
  border: none;
  font-size: 2.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  filter: grayscale(100%);
  opacity: 0.5;
}

.rating-star:hover,
.rating-star.active {
  filter: grayscale(0%);
  opacity: 1;
  transform: scale(1.1);
}

.rating-value {
  text-align: center;
  margin-top: 1rem;
  color: #666;
  font-weight: 600;
}

.yes-no-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.yes-no-btn {
  flex: 1;
  max-width: 200px;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.yes-no-btn.yes:hover,
.yes-no-btn.yes.selected {
  background: #e8f5e9;
  border-color: #2e7d32;
  color: #2e7d32;
}

.yes-no-btn.no:hover,
.yes-no-btn.no.selected {
  background: #ffebee;
  border-color: #d32f2f;
  color: #d32f2f;
}

.error-message {
  background: #ffebee;
  color: #d32f2f;
  padding: 1rem;
  border-radius: 10px;
  text-align: center;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 1rem;
}

.btn {
  padding: 1rem 2rem;
  border-radius: 10px;
  font-size: 1.1rem;
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

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

@media (max-width: 768px) {
  .question-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions .btn {
    width: 100%;
    justify-content: center;
  }

  .yes-no-buttons {
    flex-direction: column;
    align-items: center;
  }

  .yes-no-btn {
    width: 100%;
    max-width: none;
  }
}
</style>
