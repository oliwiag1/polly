/**
 * Testy jednostkowe dla ApiService
 */
import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { server } from '../../mocks/server'
import { http, HttpResponse } from 'msw'
import { QuestionType } from '@/types/survey'

// Musimy dynamicznie importować ApiService po ustawieniu mocków
let apiService: typeof import('@/services/api').apiService

const API_URL = 'http://localhost:8000'

describe('ApiService', () => {
  beforeAll(async () => {
    server.listen({ onUnhandledRequest: 'warn' })
    // Dynamiczny import po starcie serwera
    const module = await import('@/services/api')
    apiService = module.apiService
  })

  afterEach(() => {
    server.resetHandlers()
  })

  afterAll(() => {
    server.close()
  })

  describe('constructor', () => {
    it('powinien używać domyślnego URL', () => {
      expect(apiService).toBeDefined()
    })
  })

  describe('getHealth', () => {
    it('powinien pobrać status health', async () => {
      const health = await apiService.getHealth()

      expect(health.status).toBe('healthy')
      expect(health.database).toBeDefined()
    })

    it('powinien rzucić błąd przy niepowodzeniu', async () => {
      server.use(
        http.get(`${API_URL}/health`, () => {
          return HttpResponse.json({ detail: 'Service unavailable' }, { status: 503 })
        })
      )

      await expect(apiService.getHealth()).rejects.toThrow('Service unavailable')
    })
  })

  describe('getApiInfo', () => {
    it('powinien pobrać informacje o API', async () => {
      const info = await apiService.getApiInfo()

      expect(info.name).toBe('Polly Survey API')
      expect(info.version).toBe('1.0.0')
      expect(info.docs).toBe('/docs')
    })
  })

  describe('getAllSurveys', () => {
    it('powinien pobrać listę ankiet', async () => {
      const surveys = await apiService.getAllSurveys()

      expect(surveys).toHaveLength(3)
      expect(surveys[0].title).toBe('Ankieta 1')
    })

    it('powinien zwrócić pustą listę', async () => {
      server.use(
        http.get(`${API_URL}/surveys/`, () => {
          return HttpResponse.json([])
        })
      )

      const surveys = await apiService.getAllSurveys()

      expect(surveys).toHaveLength(0)
    })

    it('powinien rzucić błąd przy niepowodzeniu', async () => {
      server.use(
        http.get(`${API_URL}/surveys/`, () => {
          return HttpResponse.json({ detail: 'Server error' }, { status: 500 })
        })
      )

      await expect(apiService.getAllSurveys()).rejects.toThrow('Server error')
    })
  })

  describe('getSurvey', () => {
    it('powinien pobrać ankietę po ID', async () => {
      const survey = await apiService.getSurvey('test-123')

      expect(survey.id).toBe('test-123')
      expect(survey.title).toBeDefined()
      expect(survey.questions).toBeDefined()
    })

    it('powinien rzucić błąd dla nieistniejącej ankiety', async () => {
      await expect(apiService.getSurvey('not-found')).rejects.toThrow('Survey not found')
    })
  })

  describe('createSurvey', () => {
    it('powinien utworzyć nową ankietę', async () => {
      const surveyData = {
        title: 'Nowa ankieta',
        description: 'Opis',
        questions: [
          {
            id: 'q1',
            text: 'Pytanie?',
            type: QuestionType.TEXT,
            required: true,
          },
        ],
      }

      const survey = await apiService.createSurvey(surveyData)

      expect(survey.id).toBe('new-survey-123')
      expect(survey.title).toBe('Nowa ankieta')
    })

    it('powinien rzucić błąd przy walidacji', async () => {
      server.use(
        http.post(`${API_URL}/surveys/`, () => {
          return HttpResponse.json({ detail: 'Validation error' }, { status: 422 })
        })
      )

      await expect(
        apiService.createSurvey({
          title: '',
          description: null,
          questions: [],
        })
      ).rejects.toThrow('Validation error')
    })
  })

  describe('submitResponse', () => {
    it('powinien wysłać odpowiedź', async () => {
      const answerData = {
        answers: [{ question_id: 'q1', value: 'Odpowiedź' }],
        respondent_id: 'user-123',
      }

      const response = await apiService.submitResponse('survey-123', answerData)

      expect(response.id).toBeDefined()
      expect(response.survey_id).toBe('survey-123')
    })

    it('powinien rzucić błąd dla brakujących odpowiedzi', async () => {
      await expect(
        apiService.submitResponse('error-survey', {
          answers: [],
        })
      ).rejects.toThrow('Required question was not answered')
    })
  })

  describe('getSurveyStats', () => {
    it('powinien pobrać statystyki ankiety', async () => {
      const stats = await apiService.getSurveyStats('survey-123')

      expect(stats.survey_id).toBe('survey-123')
      expect(stats.total_responses).toBeDefined()
      expect(stats.questions_stats).toBeDefined()
    })

    it('powinien rzucić błąd dla nieistniejącej ankiety', async () => {
      await expect(apiService.getSurveyStats('not-found')).rejects.toThrow('Survey not found')
    })
  })

  describe('error handling', () => {
    it('powinien obsługiwać błąd sieciowy', async () => {
      server.use(
        http.get(`${API_URL}/health`, () => {
          return HttpResponse.error()
        })
      )

      await expect(apiService.getHealth()).rejects.toThrow()
    })

    it('powinien obsługiwać nieznany błąd', async () => {
      server.use(
        http.get(`${API_URL}/health`, () => {
          return new HttpResponse(null, { status: 500 })
        })
      )

      await expect(apiService.getHealth()).rejects.toThrow()
    })
  })
})
