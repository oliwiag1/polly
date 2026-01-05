<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '@/services/api'
import { QuestionType, type Question, type SurveyCreate } from '@/types/survey'

const router = useRouter()

const title = ref('')
const description = ref('')
const questions = ref<Question[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const questionTypeLabels: Record<QuestionType, string> = {
  [QuestionType.TEXT]: '📝 Tekst',
  [QuestionType.SINGLE_CHOICE]: '⭕ Jednokrotny wybór',
  [QuestionType.MULTIPLE_CHOICE]: '☑️ Wielokrotny wybór',
  [QuestionType.RATING]: '⭐ Ocena',
  [QuestionType.YES_NO]: '✅ Tak / Nie'
}

const isValid = computed(() => {
  return title.value.trim().length > 0 && questions.value.length > 0
})

const generateId = () => {
  return `q_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

const addQuestion = () => {
  questions.value.push({
    id: generateId(),
    text: '',
    type: QuestionType.TEXT,
    required: true,
    options: null,
    min_rating: 1,
    max_rating: 5
  })
}

const removeQuestion = (index: number) => {
  questions.value.splice(index, 1)
}

const moveQuestion = (index: number, direction: 'up' | 'down') => {
  const newIndex = direction === 'up' ? index - 1 : index + 1
  if (newIndex < 0 || newIndex >= questions.value.length) return
  
  const temp = questions.value[index]
  const newItem = questions.value[newIndex]
  if (!temp || !newItem) return
  
  questions.value[index] = newItem
  questions.value[newIndex] = temp
}

const onTypeChange = (question: Question) => {
  if (question.type === QuestionType.SINGLE_CHOICE || question.type === QuestionType.MULTIPLE_CHOICE) {
    if (!question.options || question.options.length === 0) {
      question.options = ['Opcja 1', 'Opcja 2']
    }
  } else {
    question.options = null
  }
}

const addOption = (question: Question) => {
  if (!question.options) {
    question.options = []
  }
  question.options.push(`Opcja ${question.options.length + 1}`)
}

const removeOption = (question: Question, optionIndex: number) => {
  if (question.options && question.options.length > 2) {
    question.options.splice(optionIndex, 1)
  }
}

const submitSurvey = async () => {
  if (!isValid.value) return

  try {
    loading.value = true
    error.value = null

    const surveyData: SurveyCreate = {
      title: title.value.trim(),
      description: description.value.trim() || null,
      questions: questions.value.map(q => ({
        ...q,
        text: q.text.trim()
      }))
    }

    const createdSurvey = await apiService.createSurvey(surveyData)
    router.push(`/surveys/${createdSurvey.id}/stats`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Nie udało się utworzyć ankiety'
    console.error('Error creating survey:', err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="create-survey-view">
    <div class="page-header">
      <h1>➕ Utwórz nową ankietę</h1>
      <p>Wypełnij formularz, aby stworzyć ankietę</p>
    </div>

    <form @submit.prevent="submitSurvey" class="survey-form">
      <div class="form-section">
        <h2>📋 Informacje podstawowe</h2>
        
        <div class="form-group">
          <label for="title">Tytuł ankiety *</label>
          <input
            id="title"
            v-model="title"
            type="text"
            placeholder="Np. Ankieta satysfakcji klienta"
            maxlength="200"
            required
          />
          <span class="char-count">{{ title.length }}/200</span>
        </div>

        <div class="form-group">
          <label for="description">Opis (opcjonalnie)</label>
          <textarea
            id="description"
            v-model="description"
            placeholder="Krótki opis ankiety..."
            maxlength="1000"
            rows="3"
          ></textarea>
          <span class="char-count">{{ description.length }}/1000</span>
        </div>
      </div>

      <div class="form-section">
        <div class="section-header">
          <h2>❓ Pytania</h2>
          <button type="button" @click="addQuestion" class="btn btn-add">
            ➕ Dodaj pytanie
          </button>
        </div>

        <div v-if="questions.length === 0" class="empty-questions">
          <p>Dodaj przynajmniej jedno pytanie do ankiety</p>
          <button type="button" @click="addQuestion" class="btn btn-primary">
            ➕ Dodaj pierwsze pytanie
          </button>
        </div>

        <TransitionGroup name="list" tag="div" class="questions-list">
          <div
            v-for="(question, index) in questions"
            :key="question.id"
            class="question-card"
          >
            <div class="question-header">
              <span class="question-number">Pytanie {{ index + 1 }}</span>
              <div class="question-actions">
                <button
                  type="button"
                  @click="moveQuestion(index, 'up')"
                  :disabled="index === 0"
                  class="btn-icon"
                  title="Przesuń w górę"
                >
                  ⬆️
                </button>
                <button
                  type="button"
                  @click="moveQuestion(index, 'down')"
                  :disabled="index === questions.length - 1"
                  class="btn-icon"
                  title="Przesuń w dół"
                >
                  ⬇️
                </button>
                <button
                  type="button"
                  @click="removeQuestion(index)"
                  class="btn-icon btn-delete"
                  title="Usuń pytanie"
                >
                  🗑️
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>Treść pytania *</label>
              <input
                v-model="question.text"
                type="text"
                placeholder="Wpisz treść pytania..."
                maxlength="500"
                required
              />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Typ pytania</label>
                <select v-model="question.type" @change="onTypeChange(question)">
                  <option
                    v-for="(label, type) in questionTypeLabels"
                    :key="type"
                    :value="type"
                  >
                    {{ label }}
                  </option>
                </select>
              </div>

              <div class="form-group form-checkbox">
                <label>
                  <input type="checkbox" v-model="question.required" />
                  Wymagane
                </label>
              </div>
            </div>

            <!-- Opcje dla pytań wyboru -->
            <div
              v-if="question.type === QuestionType.SINGLE_CHOICE || question.type === QuestionType.MULTIPLE_CHOICE"
              class="options-section"
            >
              <label>Opcje odpowiedzi</label>
              <div class="options-list">
                <div
                  v-for="(option, optIndex) in question.options"
                  :key="optIndex"
                  class="option-item"
                >
                  <span class="option-marker">
                    {{ question.type === QuestionType.SINGLE_CHOICE ? '○' : '☐' }}
                  </span>
                  <input
                    v-model="question.options![optIndex]"
                    type="text"
                    :placeholder="`Opcja ${optIndex + 1}`"
                  />
                  <button
                    type="button"
                    @click="removeOption(question, optIndex)"
                    :disabled="question.options!.length <= 2"
                    class="btn-icon btn-small"
                    title="Usuń opcję"
                  >
                    ✕
                  </button>
                </div>
              </div>
              <button
                type="button"
                @click="addOption(question)"
                class="btn btn-add-option"
              >
                ➕ Dodaj opcję
              </button>
            </div>

            <!-- Ustawienia oceny -->
            <div v-if="question.type === QuestionType.RATING" class="rating-section">
              <div class="form-row">
                <div class="form-group">
                  <label>Minimalna ocena</label>
                  <input
                    v-model.number="question.min_rating"
                    type="number"
                    min="0"
                    max="10"
                  />
                </div>
                <div class="form-group">
                  <label>Maksymalna ocena</label>
                  <input
                    v-model.number="question.max_rating"
                    type="number"
                    min="1"
                    max="10"
                  />
                </div>
              </div>
              <div class="rating-preview">
                <span>Podgląd: </span>
                <span
                  v-for="n in (question.max_rating || 5) - (question.min_rating || 1) + 1"
                  :key="n"
                  class="star"
                >
                  ⭐
                </span>
              </div>
            </div>
          </div>
        </TransitionGroup>
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
          :disabled="!isValid || loading"
        >
          {{ loading ? '⏳ Tworzenie...' : '✅ Utwórz ankietę' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.create-survey-view {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0;
  color: #333;
  font-size: 2rem;
}

.page-header p {
  margin: 0.5rem 0 0;
  color: #666;
}

.survey-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.form-section h2 {
  margin: 0 0 1.5rem;
  color: #333;
  font-size: 1.3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
}

.form-group {
  margin-bottom: 1.5rem;
  position: relative;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 600;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.char-count {
  position: absolute;
  right: 0;
  top: 0;
  font-size: 0.8rem;
  color: #999;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-checkbox label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  height: 100%;
  padding-top: 1.5rem;
}

.form-checkbox input[type="checkbox"] {
  width: auto;
  transform: scale(1.3);
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

.btn-add {
  background: #e8f5e9;
  color: #2e7d32;
  border: 2px solid #2e7d32;
}

.btn-add:hover {
  background: #2e7d32;
  color: white;
}

.btn-add-option {
  background: transparent;
  color: #667eea;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.btn-add-option:hover {
  background: #f0f4ff;
}

.empty-questions {
  text-align: center;
  padding: 3rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px dashed #e0e0e0;
}

.empty-questions p {
  color: #666;
  margin-bottom: 1rem;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.question-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.question-card:hover {
  border-color: #667eea;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.question-number {
  font-weight: 700;
  color: #667eea;
  font-size: 1.1rem;
}

.question-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: white;
  border: 1px solid #e0e0e0;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover:not(:disabled) {
  background: #f0f4ff;
  border-color: #667eea;
}

.btn-icon:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-delete:hover:not(:disabled) {
  background: #ffebee;
  border-color: #d32f2f;
}

.btn-small {
  padding: 0.2rem 0.5rem;
  font-size: 0.8rem;
}

.options-section,
.rating-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.option-marker {
  font-size: 1.2rem;
  color: #667eea;
}

.option-item input {
  flex: 1;
}

.rating-preview {
  margin-top: 1rem;
  color: #666;
}

.star {
  font-size: 1.2rem;
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

/* Animacje listy */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
