/**
 * Testy integracyjne dla przepływów użytkownika
 */
import { describe, it, expect, beforeAll, afterAll, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createWebHistory, createMemoryHistory } from 'vue-router'
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
import { QuestionType } from '@/types/survey'

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

describe('Integracja: Przepływy użytkownika', () => {
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' })
  })

  afterEach(() => {
    server.resetHandlers()
  })

  afterAll(() => {
    server.close()
  })

  describe('Przepływ: Przeglądanie ankiet', () => {
    it('powinien przejść z Home -> Lista ankiet -> Szczegóły ankiety', async () => {
      const router = createTestRouter()
      
      const wrapper = mount(App, {
        global: { plugins: [router] },
      })

      // Start na stronie głównej
      await router.push('/')
      await flushPromises()
      expect(wrapper.text()).toContain('Polly')

      // Przejdź do listy ankiet
      await router.push('/surveys')
      await flushPromises()
      expect(wrapper.text()).toContain('Lista ankiet')

      // Przejdź do wypełniania ankiety
      await router.push('/surveys/test-123')
      await flushPromises()
      expect(wrapper.text()).toContain('Testowa Ankieta')
    })

    it('powinien przejść z listy do statystyk', async () => {
      const router = createTestRouter()
      
      const wrapper = mount(App, {
        global: { plugins: [router] },
      })

      await router.push('/surveys')
      await flushPromises()

      await router.push('/surveys/test-123/stats')
      await flushPromises()

      expect(wrapper.text()).toContain('Statystyki')
    })
  })

  describe('Przepływ: Tworzenie ankiety', () => {
    it('powinien przejść Home -> Tworzenie -> Statystyki', async () => {
      const createdSurveyId = 'new-survey-123'
      
      server.use(
        http.post(`${API_URL}/surveys/`, () => {
          return HttpResponse.json(createMockSurvey({ id: createdSurveyId }))
        })
      )

      const router = createTestRouter()
      const wrapper = mount(App, {
        global: { plugins: [router] },
      })

      // Start na Home
      await router.push('/')
      await flushPromises()

      // Przejdź do tworzenia
      await router.push('/surveys/create')
      await flushPromises()
      expect(wrapper.text()).toContain('Utwórz')

      // Po stworzeniu przejdź do statystyk
      await router.push(`/surveys/${createdSurveyId}/stats`)
      await flushPromises()
      expect(wrapper.text()).toContain('Statystyki')
    })
  })

  describe('Przepływ: Wypełnianie ankiety', () => {
    it('powinien przejść Ankieta -> Sukces -> Home', async () => {
      server.use(
        http.get(`${API_URL}/surveys/:id`, () => {
          return HttpResponse.json(createMockSurvey({
            id: 'survey-1',
            questions: [
              { id: 'q1', text: 'Imię?', type: QuestionType.TEXT, required: false }
            ]
          }))
        }),
        http.post(`${API_URL}/surveys/:id/responses`, () => {
          return HttpResponse.json({ message: 'OK', response_id: 'resp-1' })
        })
      )

      const router = createTestRouter()
      const wrapper = mount(App, {
        global: { plugins: [router] },
      })

      // Wypełnianie ankiety
      await router.push('/surveys/survey-1')
      await flushPromises()
      expect(wrapper.text()).toContain('Testowa Ankieta')

      // Po wysłaniu - sukces
      await router.push('/surveys/survey-1/success')
      await flushPromises()
      expect(wrapper.text()).toContain('Dziękujemy')

      // Powrót do Home
      await router.push('/')
      await flushPromises()
      expect(wrapper.text()).toContain('Polly')
    })
  })

  describe('Przepływ: Obsługa błędów', () => {
    it('powinien obsłużyć błąd 404 gracefully', async () => {
      const router = createTestRouter()
      const wrapper = mount(App, {
        global: { plugins: [router] },
      })

      await router.push('/surveys/not-found')
      await flushPromises()

      expect(wrapper.text()).toContain('Błąd')
    })

    it('powinien obsłużyć błąd serwera', async () => {
      server.use(
        http.get(`${API_URL}/surveys/`, () => {
          return HttpResponse.json({ detail: 'Internal error' }, { status: 500 })
        })
      )

      const router = createTestRouter()
      const wrapper = mount(App, {
        global: { plugins: [router] },
      })

      await router.push('/surveys')
      await flushPromises()

      expect(wrapper.text()).toContain('Błąd')
    })
  })
})

describe('Integracja: API Service z komponentami', () => {
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' })
  })

  afterEach(() => {
    server.resetHandlers()
  })

  afterAll(() => {
    server.close()
  })

  it('powinien poprawnie pobierać i wyświetlać listę ankiet', async () => {
    server.use(
      http.get(`${API_URL}/surveys/`, () => {
        return HttpResponse.json([
          createMockSurvey({ id: '1', title: 'Ankieta A' }),
          createMockSurvey({ id: '2', title: 'Ankieta B' }),
          createMockSurvey({ id: '3', title: 'Ankieta C' }),
        ])
      })
    )

    const router = createTestRouter()
    const wrapper = mount(SurveysListView, {
      global: { plugins: [router] },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('Ankieta A')
    expect(wrapper.text()).toContain('Ankieta B')
    expect(wrapper.text()).toContain('Ankieta C')
  })

  it('powinien poprawnie pobierać i wyświetlać szczegóły ankiety', async () => {
    const testSurvey = createMockSurvey({
      id: 'detailed-survey',
      title: 'Szczegółowa ankieta',
      description: 'Unikalny opis',
      questions: [
        { id: 'q1', text: 'Pytanie specjalne?', type: QuestionType.TEXT, required: true }
      ]
    })

    server.use(
      http.get(`${API_URL}/surveys/:id`, () => {
        return HttpResponse.json(testSurvey)
      })
    )

    const router = createTestRouter()
    await router.push('/surveys/detailed-survey')
    
    const wrapper = mount(FillSurveyView, {
      global: { plugins: [router] },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('Szczegółowa ankieta')
    expect(wrapper.text()).toContain('Unikalny opis')
    expect(wrapper.text()).toContain('Pytanie specjalne?')
  })

  it('powinien poprawnie pobierać i wyświetlać statystyki', async () => {
    const stats = createMockSurveyStats({
      survey_title: 'Ankieta statystyczna',
      total_responses: 42,
    })

    server.use(
      http.get(`${API_URL}/surveys/:id/stats`, () => {
        return HttpResponse.json(stats)
      })
    )

    const router = createTestRouter()
    await router.push('/surveys/stat-survey/stats')
    
    const wrapper = mount(SurveyStatsView, {
      global: { plugins: [router] },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('Ankieta statystyczna')
    expect(wrapper.text()).toContain('42')
  })
})

describe('Integracja: Router guards i nawigacja', () => {
  it('powinien poprawnie nawigować między wszystkimi widokami', async () => {
    const router = createTestRouter()
    const visitedRoutes: string[] = []

    router.afterEach((to) => {
      visitedRoutes.push(to.path)
    })

    await router.push('/')
    await router.push('/surveys')
    await router.push('/surveys/create')
    await router.push('/surveys/test-id')
    await router.push('/surveys/test-id/stats')
    await router.push('/surveys/test-id/success')

    expect(visitedRoutes).toEqual([
      '/',
      '/surveys',
      '/surveys/create',
      '/surveys/test-id',
      '/surveys/test-id/stats',
      '/surveys/test-id/success',
    ])
  })

  it('powinien poprawnie obsługiwać parametry route', async () => {
    const router = createTestRouter()

    await router.push('/surveys/my-custom-id')
    expect(router.currentRoute.value.params.id).toBe('my-custom-id')

    await router.push('/surveys/another-id/stats')
    expect(router.currentRoute.value.params.id).toBe('another-id')
  })
})
