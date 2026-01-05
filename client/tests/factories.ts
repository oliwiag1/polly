/**
 * Fabryki danych testowych
 */
import { QuestionType, type Survey, type Question, type SurveyStats, type QuestionStats, type HealthStatus, type ApiInfo, type SurveyResponse, type Answer } from '@/types/survey'

export const createMockQuestion = (overrides: Partial<Question> = {}): Question => ({
  id: `q_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  text: 'Przykładowe pytanie?',
  type: QuestionType.TEXT,
  required: true,
  options: null,
  min_rating: null,
  max_rating: null,
  ...overrides,
})

export const createMockSurvey = (overrides: Partial<Survey> = {}): Survey => {
  const id = overrides.id || 'test-survey-123'
  return {
    id,
    title: 'Testowa Ankieta',
    description: 'Opis testowej ankiety',
    questions: [
      createMockQuestion({ id: 'q1', text: 'Jak masz na imię?', type: QuestionType.TEXT }),
      createMockQuestion({ 
        id: 'q2', 
        text: 'Ulubiony kolor?', 
        type: QuestionType.SINGLE_CHOICE,
        options: ['Czerwony', 'Niebieski', 'Zielony'],
      }),
    ],
    created_at: '2026-01-05T12:00:00Z',
    links: {
      survey_url: `http://localhost:8000/surveys/${id}`,
      stats_url: `http://localhost:8000/surveys/${id}/stats`,
    },
    ...overrides,
  }
}

export const createMockQuestionStats = (overrides: Partial<QuestionStats> = {}): QuestionStats => ({
  question_id: 'q1',
  question_text: 'Przykładowe pytanie?',
  question_type: QuestionType.TEXT,
  total_responses: 10,
  answer_distribution: { 'Odpowiedź 1': 5, 'Odpowiedź 2': 5 },
  average_value: null,
  ...overrides,
})

export const createMockSurveyStats = (overrides: Partial<SurveyStats> = {}): SurveyStats => ({
  survey_id: 'test-survey-123',
  survey_title: 'Testowa Ankieta',
  total_responses: 25,
  questions_stats: [
    createMockQuestionStats({ question_id: 'q1', question_text: 'Pytanie 1' }),
    createMockQuestionStats({ question_id: 'q2', question_text: 'Pytanie 2' }),
  ],
  created_at: '2026-01-05T12:00:00Z',
  last_response_at: '2026-01-05T14:30:00Z',
  ...overrides,
})

export const createMockHealthStatus = (overrides: Partial<HealthStatus> = {}): HealthStatus => ({
  status: 'healthy',
  database: {
    surveys: 10,
    responses: 50,
  },
  ...overrides,
})

export const createMockApiInfo = (overrides: Partial<ApiInfo> = {}): ApiInfo => ({
  name: 'Polly Survey API',
  version: '1.0.0',
  docs: '/docs',
  redoc: '/redoc',
  ...overrides,
})

export const createMockSurveyResponse = (overrides: Partial<SurveyResponse> = {}): SurveyResponse => ({
  id: 'response-123',
  survey_id: 'test-survey-123',
  answers: [
    { question_id: 'q1', value: 'Jan Kowalski' },
    { question_id: 'q2', value: 'Niebieski' },
  ],
  respondent_id: 'user-123',
  submitted_at: '2026-01-05T14:00:00Z',
  ...overrides,
})

export const createMockAnswer = (overrides: Partial<Answer> = {}): Answer => ({
  question_id: 'q1',
  value: 'Przykładowa odpowiedź',
  ...overrides,
})

// Wszystkie typy pytań
export const allQuestionTypes: Question[] = [
  createMockQuestion({ id: 'q_text', text: 'Pytanie tekstowe', type: QuestionType.TEXT }),
  createMockQuestion({ 
    id: 'q_single', 
    text: 'Jednokrotny wybór', 
    type: QuestionType.SINGLE_CHOICE,
    options: ['Opcja A', 'Opcja B', 'Opcja C'],
  }),
  createMockQuestion({ 
    id: 'q_multi', 
    text: 'Wielokrotny wybór', 
    type: QuestionType.MULTIPLE_CHOICE,
    options: ['Opcja 1', 'Opcja 2', 'Opcja 3'],
    required: false,
  }),
  createMockQuestion({ 
    id: 'q_rating', 
    text: 'Oceń nas', 
    type: QuestionType.RATING,
    min_rating: 1,
    max_rating: 5,
  }),
  createMockQuestion({ 
    id: 'q_yesno', 
    text: 'Tak czy nie?', 
    type: QuestionType.YES_NO,
  }),
]

export const createSurveyWithAllQuestionTypes = (): Survey => 
  createMockSurvey({
    id: 'full-survey',
    title: 'Ankieta ze wszystkimi typami pytań',
    questions: allQuestionTypes,
  })
