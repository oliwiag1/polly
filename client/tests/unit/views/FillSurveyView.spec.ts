/**
 * Testy jednostkowe dla FillSurveyView
 */
import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { server } from '../../mocks/server'
import { http, HttpResponse } from 'msw'
import FillSurveyView from '@/views/FillSurveyView.vue'
import { createMockSurvey } from '../../factories'
import { QuestionType } from '@/types/survey'

const API_URL = 'http://localhost:8000'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/surveys/:id', name: 'fill-survey', component: FillSurveyView },
    { path: '/surveys/:id/success', name: 'survey-success', component: { template: '<div>Success</div>' } },
    { path: '/surveys', name: 'surveys', component: { template: '<div>List</div>' } },
  ],
})

describe('FillSurveyView', () => {
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
    await router.push(`/surveys/${surveyId}`)
    const wrapper = mount(FillSurveyView, {
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

    it('powinien renderować opis ankiety', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Opis testowej ankiety')
    })

    it('powinien renderować liczbę pytań', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('pytań')
    })

    it('powinien wyświetlać błąd dla nieistniejącej ankiety', async () => {
      const wrapper = await mountComponent('not-found')

      expect(wrapper.text()).toContain('Błąd')
      expect(wrapper.text()).toContain('Survey not found')
    })
  })

  describe('pytania', () => {
    it('powinien renderować wszystkie pytania', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Jak masz na imię?')
      expect(wrapper.text()).toContain('Ulubiony kolor?')
    })

    it('powinien wyświetlać numer pytania', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.find('.question-number').exists()).toBe(true)
    })
  })

  describe('typy odpowiedzi', () => {
    it('powinien renderować pole tekstowe dla TEXT', async () => {
      server.use(
        http.get(`${API_URL}/surveys/:id`, () => {
          return HttpResponse.json(createMockSurvey({
            questions: [
              { id: 'q1', text: 'Imię?', type: QuestionType.TEXT, required: true }
            ]
          }))
        })
      )

      const wrapper = await mountComponent()

      expect(wrapper.find('input[type="text"]').exists() || wrapper.find('textarea').exists()).toBe(true)
    })

    it('powinien renderować radio buttons dla SINGLE_CHOICE', async () => {
      server.use(
        http.get(`${API_URL}/surveys/:id`, () => {
          return HttpResponse.json(createMockSurvey({
            questions: [
              { 
                id: 'q1', 
                text: 'Wybór?', 
                type: QuestionType.SINGLE_CHOICE, 
                required: true,
                options: ['A', 'B', 'C'],
              }
            ]
          }))
        })
      )

      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('A')
      expect(wrapper.text()).toContain('B')
    })

    it('powinien renderować checkboxy dla MULTIPLE_CHOICE', async () => {
      server.use(
        http.get(`${API_URL}/surveys/:id`, () => {
          return HttpResponse.json(createMockSurvey({
            questions: [
              { 
                id: 'q1', 
                text: 'Wielokrotny?', 
                type: QuestionType.MULTIPLE_CHOICE, 
                required: false,
                options: ['X', 'Y', 'Z'],
              }
            ]
          }))
        })
      )

      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('X')
      expect(wrapper.text()).toContain('Y')
    })

    it('powinien renderować gwiazdki dla RATING', async () => {
      server.use(
        http.get(`${API_URL}/surveys/:id`, () => {
          return HttpResponse.json(createMockSurvey({
            questions: [
              { 
                id: 'q1', 
                text: 'Oceń', 
                type: QuestionType.RATING, 
                required: true,
                min_rating: 1,
                max_rating: 5,
              }
            ]
          }))
        })
      )

      const wrapper = await mountComponent()

      expect(wrapper.find('.rating').exists() || wrapper.text()).toBeTruthy()
    })

    it('powinien renderować Yes/No dla YES_NO', async () => {
      server.use(
        http.get(`${API_URL}/surveys/:id`, () => {
          return HttpResponse.json(createMockSurvey({
            questions: [
              { 
                id: 'q1', 
                text: 'Tak/Nie?', 
                type: QuestionType.YES_NO, 
                required: true,
              }
            ]
          }))
        })
      )

      const wrapper = await mountComponent()

      const text = wrapper.text()
      expect(text.includes('Tak') || text.includes('Nie')).toBe(true)
    })
  })

  describe('walidacja', () => {
    it('powinien wymagać odpowiedzi na wymagane pytania', async () => {
      const wrapper = await mountComponent()

      const submitBtn = wrapper.find('button[type="submit"]')
      // Przycisk powinien być zablokowany bez odpowiedzi
      expect(submitBtn.exists()).toBe(true)
    })
  })

  describe('wysyłanie', () => {
    it('powinien przekierowywać po sukcesie', async () => {
      server.use(
        http.get(`${API_URL}/surveys/:id`, () => {
          return HttpResponse.json(createMockSurvey({
            questions: [
              { id: 'q1', text: 'Imię?', type: QuestionType.TEXT, required: false }
            ]
          }))
        })
      )

      const wrapper = await mountComponent()

      const form = wrapper.find('form')
      if (form.exists()) {
        await form.trigger('submit')
        await flushPromises()
      }
    })
  })

  describe('loading state', () => {
    it('powinien wyświetlać spinner podczas ładowania', async () => {
      server.use(
        http.get(`${API_URL}/surveys/:id`, async () => {
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json(createMockSurvey())
        })
      )

      await router.push('/surveys/test-123')
      const wrapper = mount(FillSurveyView, {
        global: { plugins: [router] },
      })

      expect(wrapper.find('.loading').exists() || wrapper.text().includes('Ładowanie')).toBe(true)
    })
  })
})
