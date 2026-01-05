/**
 * Testy jednostkowe dla SurveyStatsView
 */
import { describe, it, expect, beforeAll, afterAll, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { server } from '../../mocks/server'
import { http, HttpResponse } from 'msw'
import SurveyStatsView from '@/views/SurveyStatsView.vue'
import { createMockSurveyStats } from '../../factories'
import { QuestionType } from '@/types/survey'

const API_URL = 'http://localhost:8000'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/surveys/:id/stats', name: 'survey-stats', component: SurveyStatsView },
    { path: '/surveys/:id', name: 'fill-survey', component: { template: '<div>Fill</div>' } },
    { path: '/surveys', name: 'surveys', component: { template: '<div>List</div>' } },
  ],
})

describe('SurveyStatsView', () => {
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' })
  })

  afterEach(() => {
    server.resetHandlers()
  })

  afterAll(() => {
    server.close()
  })

  const mountComponent = async (surveyId: string = 'test-123') => {
    await router.push(`/surveys/${surveyId}/stats`)
    const wrapper = mount(SurveyStatsView, {
      global: {
        plugins: [router],
      },
    })
    await flushPromises()
    return wrapper
  }

  describe('rendering', () => {
    it('powinien renderować tytuł ankiety', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Testowa Ankieta')
    })

    it('powinien renderować statystyki', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Statystyki')
    })

    it('powinien wyświetlać liczbę odpowiedzi', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('25') // total_responses
      expect(wrapper.text()).toContain('Odpowiedzi')
    })

    it('powinien wyświetlać liczbę pytań', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('2') // liczba pytań
      expect(wrapper.text()).toContain('Pytań')
    })
  })

  describe('daty', () => {
    it('powinien wyświetlać datę utworzenia', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Data utworzenia')
    })

    it('powinien wyświetlać datę ostatniej odpowiedzi', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Ostatnia odpowiedź')
    })
  })

  describe('udostępnianie', () => {
    it('powinien wyświetlać sekcję udostępniania', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Udostępnij')
    })

    it('powinien mieć przycisk kopiowania', async () => {
      const wrapper = await mountComponent()

      const copyBtn = wrapper.find('.btn-copy')
      expect(copyBtn.exists()).toBe(true)
    })

    it('powinien kopiować link do schowka', async () => {
      const wrapper = await mountComponent()

      const copyBtn = wrapper.find('.btn-copy')
      await copyBtn.trigger('click')

      expect(navigator.clipboard.writeText).toHaveBeenCalled()
    })
  })

  describe('błędy', () => {
    it('powinien wyświetlać błąd dla nieistniejącej ankiety', async () => {
      const wrapper = await mountComponent('not-found')

      expect(wrapper.text()).toContain('Błąd')
    })

    it('powinien mieć przycisk powrotu przy błędzie', async () => {
      const wrapper = await mountComponent('not-found')

      expect(wrapper.text()).toContain('Wróć do listy')
    })
  })

  describe('odświeżanie', () => {
    it('powinien mieć przycisk odświeżania', async () => {
      const wrapper = await mountComponent()

      const refreshBtn = wrapper.find('.btn-refresh')
      expect(refreshBtn.exists()).toBe(true)
    })

    it('powinien odświeżać statystyki po kliknięciu', async () => {
      const wrapper = await mountComponent()

      const refreshBtn = wrapper.find('.btn-refresh')
      await refreshBtn.trigger('click')
      await flushPromises()

      expect(wrapper.text()).toContain('25')
    })
  })

  describe('statystyki pytań', () => {
    it('powinien wyświetlać statystyki dla każdego pytania', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Pytanie 1')
      expect(wrapper.text()).toContain('Pytanie 2')
    })

    it('powinien wyświetlać rozkład odpowiedzi', async () => {
      server.use(
        http.get(`${API_URL}/surveys/:id/stats`, () => {
          return HttpResponse.json(createMockSurveyStats({
            questions_stats: [
              {
                question_id: 'q1',
                question_text: 'Test?',
                question_type: QuestionType.SINGLE_CHOICE,
                total_responses: 10,
                answer_distribution: { 'Tak': 7, 'Nie': 3 },
                average_value: null,
              }
            ]
          }))
        })
      )

      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Tak')
      expect(wrapper.text()).toContain('Nie')
    })

    it('powinien wyświetlać średnią dla pytań z oceną', async () => {
      server.use(
        http.get(`${API_URL}/surveys/:id/stats`, () => {
          return HttpResponse.json(createMockSurveyStats({
            questions_stats: [
              {
                question_id: 'q1',
                question_text: 'Oceń',
                question_type: QuestionType.RATING,
                total_responses: 10,
                answer_distribution: { '4': 5, '5': 5 },
                average_value: 4.5,
              }
            ]
          }))
        })
      )

      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('4.5') || expect(wrapper.text()).toContain('Średnia')
    })
  })

  describe('nawigacja', () => {
    it('powinien mieć link do wypełnienia ankiety', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Wypełnij ankietę')
    })
  })

  describe('loading state', () => {
    it('powinien wyświetlać spinner podczas ładowania', async () => {
      server.use(
        http.get(`${API_URL}/surveys/:id/stats`, async () => {
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json(createMockSurveyStats())
        })
      )

      await router.push('/surveys/test-123/stats')
      const wrapper = mount(SurveyStatsView, {
        global: { plugins: [router] },
      })

      expect(wrapper.find('.loading').exists() || wrapper.text().includes('Ładowanie')).toBe(true)
    })
  })
})
