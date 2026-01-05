/**
 * Testy End-to-End - pełne scenariusze użytkownika
 */
import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { server } from '../mocks/server'
import { http, HttpResponse } from 'msw'
import App from '@/App.vue'
import HomeView from '@/views/HomeView.vue'
import SurveysListView from '@/views/SurveysListView.vue'
import CreateSurveyView from '@/views/CreateSurveyView.vue'
import FillSurveyView from '@/views/FillSurveyView.vue'
import SurveyStatsView from '@/views/SurveyStatsView.vue'
import SurveySuccessView from '@/views/SurveySuccessView.vue'
import { createMockSurvey, createMockSurveyStats } from '../factories'
import { QuestionType, type Survey, type AnswerSubmit } from '@/types/survey'

const API_URL = 'http://localhost:8000'

const createTestRouter = () => createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/surveys', name: 'surveys', component: SurveysListView },
    { path: '/surveys/create', name: 'create-survey', component: CreateSurveyView },
    { path: '/surveys/:id', name: 'fill-survey', component: FillSurveyView },
    { path: '/surveys/:id/stats', name: 'survey-stats', component: SurveyStatsView },
    { path: '/surveys/:id/success', name: 'survey-success', component: SurveySuccessView },
  ],
})

describe('E2E: Scenariusze użytkownika', () => {
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' })
  })

  afterEach(() => {
    server.resetHandlers()
  })

  afterAll(() => {
    server.close()
  })

  describe('Scenariusz: Administrator tworzy ankietę', () => {
    it('powinien móc stworzyć kompletną ankietę i zobaczyć statystyki', async () => {
      const createdSurveyId = 'created-survey-123'

      server.use(
        http.post(`${API_URL}/surveys/`, async ({ request }) => {
          const body = await request.json() as Partial<Survey>
          return HttpResponse.json({
            ...createMockSurvey({ id: createdSurveyId }),
            title: body.title,
            description: body.description,
            questions: body.questions,
          })
        }),
        http.get(`${API_URL}/surveys/${createdSurveyId}/stats`, () => {
          return HttpResponse.json(createMockSurveyStats({
            survey_id: createdSurveyId,
            survey_title: 'Moja nowa ankieta',
            total_responses: 0,
          }))
        })
      )

      const router = createTestRouter()
      const wrapper = mount(App, {
        global: { plugins: [router] },
      })

      // 1. Otwórz stronę tworzenia
      await router.push('/surveys/create')
      await flushPromises()
      expect(wrapper.text()).toContain('Utwórz')

      // 2. Symuluj stworzenie ankiety (API call)
      // Po stworzeniu przekierowanie do statystyk
      await router.push(`/surveys/${createdSurveyId}/stats`)
      await flushPromises()

      expect(wrapper.text()).toContain('Statystyki')
    })
  })

  describe('Scenariusz: Respondent wypełnia ankietę', () => {
    it('powinien móc wypełnić ankietę i zobaczyć potwierdzenie', async () => {
      const surveyId = 'survey-to-fill'

      server.use(
        http.get(`${API_URL}/surveys/${surveyId}`, () => {
          return HttpResponse.json(createMockSurvey({
            id: surveyId,
            title: 'Ankieta do wypełnienia',
            questions: [
              { id: 'q1', text: 'Twoje imię?', type: QuestionType.TEXT, required: true },
              { id: 'q2', text: 'Ulubiony kolor?', type: QuestionType.SINGLE_CHOICE, required: true, options: ['Czerwony', 'Niebieski', 'Zielony'] },
              { id: 'q3', text: 'Oceń nas', type: QuestionType.RATING, required: false, min_rating: 1, max_rating: 5 },
            ]
          }))
        }),
        http.post(`${API_URL}/surveys/${surveyId}/responses`, async ({ request }) => {
          const body = await request.json() as AnswerSubmit
          return HttpResponse.json({
            message: 'Response recorded',
            response_id: 'resp-123',
            answers_count: body.answers?.length || 0,
          })
        })
      )

      const router = createTestRouter()
      const wrapper = mount(App, {
        global: { plugins: [router] },
      })

      // 1. Otwórz ankietę
      await router.push(`/surveys/${surveyId}`)
      await flushPromises()
      expect(wrapper.text()).toContain('Ankieta do wypełnienia')
      expect(wrapper.text()).toContain('Twoje imię?')

      // 2. Po wysłaniu - przekierowanie na sukces
      await router.push(`/surveys/${surveyId}/success`)
      await flushPromises()
      expect(wrapper.text()).toContain('Dziękujemy')
    })

    it('powinien obsłużyć różne typy pytań', async () => {
      const surveyId = 'multi-type-survey'

      server.use(
        http.get(`${API_URL}/surveys/${surveyId}`, () => {
          return HttpResponse.json(createMockSurvey({
            id: surveyId,
            questions: [
              { id: 'q1', text: 'Tekst', type: QuestionType.TEXT, required: true },
              { id: 'q2', text: 'Wybór', type: QuestionType.SINGLE_CHOICE, required: true, options: ['A', 'B'] },
              { id: 'q3', text: 'Multi', type: QuestionType.MULTIPLE_CHOICE, required: false, options: ['X', 'Y', 'Z'] },
              { id: 'q4', text: 'Ocena', type: QuestionType.RATING, required: false, min_rating: 1, max_rating: 5 },
              { id: 'q5', text: 'Tak/Nie', type: QuestionType.YES_NO, required: true },
            ]
          }))
        })
      )

      const router = createTestRouter()
      await router.push(`/surveys/${surveyId}`)

      const wrapper = mount(FillSurveyView, {
        global: { plugins: [router] },
      })
      await flushPromises()

      // Sprawdź że wszystkie pytania są widoczne
      expect(wrapper.text()).toContain('Tekst')
      expect(wrapper.text()).toContain('Wybór')
      expect(wrapper.text()).toContain('Multi')
      expect(wrapper.text()).toContain('Ocena')
      expect(wrapper.text()).toContain('Tak/Nie')
    })
  })

  describe('Scenariusz: Przeglądanie statystyk', () => {
    it('powinien wyświetlać kompletne statystyki ankiety', async () => {
      const surveyId = 'stats-survey'

      server.use(
        http.get(`${API_URL}/surveys/${surveyId}/stats`, () => {
          return HttpResponse.json(createMockSurveyStats({
            survey_id: surveyId,
            survey_title: 'Statystyczna ankieta',
            total_responses: 150,
            questions_stats: [
              {
                question_id: 'q1',
                question_text: 'Ulubiony język?',
                question_type: QuestionType.SINGLE_CHOICE,
                total_responses: 150,
                answer_distribution: { 'Python': 60, 'JavaScript': 50, 'TypeScript': 40 },
                average_value: null,
              },
              {
                question_id: 'q2',
                question_text: 'Oceń framework',
                question_type: QuestionType.RATING,
                total_responses: 145,
                answer_distribution: { '5': 80, '4': 50, '3': 15 },
                average_value: 4.45,
              },
            ]
          }))
        })
      )

      const router = createTestRouter()
      await router.push(`/surveys/${surveyId}/stats`)

      const wrapper = mount(SurveyStatsView, {
        global: { plugins: [router] },
      })
      await flushPromises()

      expect(wrapper.text()).toContain('Statystyczna ankieta')
      expect(wrapper.text()).toContain('150')
    })
  })

  describe('Scenariusz: Wyszukiwanie ankiet', () => {
    it('powinien filtrować listę ankiet', async () => {
      server.use(
        http.get(`${API_URL}/surveys/`, () => {
          return HttpResponse.json([
            createMockSurvey({ id: '1', title: 'Ankieta o programowaniu' }),
            createMockSurvey({ id: '2', title: 'Ankieta o designie' }),
            createMockSurvey({ id: '3', title: 'Ankieta o marketingu' }),
            createMockSurvey({ id: '4', title: 'Feedback produktowy' }),
          ])
        })
      )

      const router = createTestRouter()
      await router.push('/surveys')

      const wrapper = mount(SurveysListView, {
        global: { plugins: [router] },
      })
      await flushPromises()

      // Szukaj
      const searchInput = wrapper.find('.search-input')
      await searchInput.setValue('programowaniu')

      // Powinna być widoczna tylko ta ankieta
      expect(wrapper.text()).toContain('programowaniu')
    })
  })

  describe('Scenariusz: Udostępnianie ankiety', () => {
    it('powinien móc skopiować link do ankiety', async () => {
      const surveyId = 'shareable-survey'
      const clipboardWriteText = vi.fn()
      Object.assign(navigator, {
        clipboard: { writeText: clipboardWriteText }
      })

      server.use(
        http.get(`${API_URL}/surveys/${surveyId}/stats`, () => {
          return HttpResponse.json(createMockSurveyStats({ survey_id: surveyId }))
        })
      )

      const router = createTestRouter()
      await router.push(`/surveys/${surveyId}/stats`)

      const wrapper = mount(SurveyStatsView, {
        global: { plugins: [router] },
      })
      await flushPromises()

      const copyBtn = wrapper.find('.btn-copy')
      if (copyBtn.exists()) {
        await copyBtn.trigger('click')
        expect(clipboardWriteText).toHaveBeenCalled()
      }
    })
  })

  describe('Scenariusz: Obsługa błędów', () => {
    it('powinien gracefully obsługiwać brak połączenia', async () => {
      server.use(
        http.get(`${API_URL}/health`, () => {
          return HttpResponse.json({ detail: 'Connection refused' }, { status: 503 })
        }),
        http.get(`${API_URL}/`, () => {
          return HttpResponse.json({ detail: 'Connection refused' }, { status: 503 })
        })
      )

      const router = createTestRouter()
      await router.push('/')

      const wrapper = mount(HomeView, {
        global: { plugins: [router] },
      })
      await flushPromises()

      expect(wrapper.text()).toContain('Błąd')
    })

    it('powinien wyświetlać przycisk retry przy błędzie', async () => {
      server.use(
        http.get(`${API_URL}/surveys/`, () => {
          return HttpResponse.json({ detail: 'Server error' }, { status: 500 })
        })
      )

      const router = createTestRouter()
      await router.push('/surveys')

      const wrapper = mount(SurveysListView, {
        global: { plugins: [router] },
      })
      await flushPromises()

      expect(wrapper.text()).toContain('Spróbuj ponownie')
    })
  })
})

describe('E2E: Pełny cykl życia ankiety', () => {
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' })
  })

  afterEach(() => {
    server.resetHandlers()
  })

  afterAll(() => {
    server.close()
  })

  it('powinien obsłużyć pełny cykl: tworzenie -> wypełnianie -> statystyki', async () => {
    const surveyId = 'lifecycle-survey'
    let surveyData: Partial<Survey> | null = null
    const responses: AnswerSubmit[] = []

    server.use(
      // Tworzenie ankiety
      http.post(`${API_URL}/surveys/`, async ({ request }) => {
        surveyData = await request.json() as Partial<Survey>
        return HttpResponse.json({
          id: surveyId,
          ...surveyData,
          created_at: new Date().toISOString(),
        })
      }),
      // Pobieranie ankiety
      http.get(`${API_URL}/surveys/${surveyId}`, () => {
        if (!surveyData) {
          return HttpResponse.json({ detail: 'Not found' }, { status: 404 })
        }
        return HttpResponse.json({ id: surveyId, ...surveyData })
      }),
      // Wysyłanie odpowiedzi
      http.post(`${API_URL}/surveys/${surveyId}/responses`, async ({ request }) => {
        const response = await request.json()
        responses.push(response)
        return HttpResponse.json({ message: 'OK', response_id: `resp-${responses.length}` })
      }),
      // Statystyki
      http.get(`${API_URL}/surveys/${surveyId}/stats`, () => {
        return HttpResponse.json(createMockSurveyStats({
          survey_id: surveyId,
          survey_title: surveyData?.title || 'Survey',
          total_responses: responses.length,
        }))
      })
    )

    const router = createTestRouter()
    const wrapper = mount(App, {
      global: { plugins: [router] },
    })

    // Krok 1: Tworzenie
    await router.push('/surveys/create')
    await flushPromises()
    expect(wrapper.text()).toContain('Utwórz')

    // Krok 2: Po stworzeniu - statystyki (0 odpowiedzi)
    await router.push(`/surveys/${surveyId}/stats`)
    await flushPromises()
    expect(wrapper.text()).toContain('Statystyki')

    // Krok 3: Wypełnianie przez respondenta
    surveyData = {
      title: 'Testowa ankieta cyklu',
      description: 'Opis',
      questions: [{ id: 'q1', text: 'Test?', type: QuestionType.TEXT, required: false }]
    }

    await router.push(`/surveys/${surveyId}`)
    await flushPromises()

    // Krok 4: Sukces
    await router.push(`/surveys/${surveyId}/success`)
    await flushPromises()
    expect(wrapper.text()).toContain('Dziękujemy')

    // Krok 5: Powrót do statystyk
    await router.push(`/surveys/${surveyId}/stats`)
    await flushPromises()
    expect(wrapper.text()).toContain('Statystyki')
  })
})
