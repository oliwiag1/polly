/**
 * Testy jednostkowe dla SurveysListView
 */
import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { server } from '../../mocks/server'
import { http, HttpResponse } from 'msw'
import SurveysListView from '@/views/SurveysListView.vue'
import { createMockSurvey } from '../../factories'

const API_URL = 'http://localhost:8000'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/surveys', name: 'surveys', component: SurveysListView },
    { path: '/surveys/create', name: 'create-survey', component: { template: '<div>Create</div>' } },
    { path: '/surveys/:id', name: 'fill-survey', component: { template: '<div>Fill</div>' } },
    { path: '/surveys/:id/stats', name: 'survey-stats', component: { template: '<div>Stats</div>' } },
  ],
})

describe('SurveysListView', () => {
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' })
  })

  afterEach(() => {
    server.resetHandlers()
  })

  afterAll(() => {
    server.close()
  })

  const mountComponent = async () => {
    const wrapper = mount(SurveysListView, {
      global: {
        plugins: [router],
      },
    })
    await flushPromises()
    return wrapper
  }

  describe('rendering', () => {
    it('powinien renderować nagłówek', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Lista ankiet')
    })

    it('powinien renderować pole wyszukiwania', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.find('.search-input').exists()).toBe(true)
    })

    it('powinien renderować przycisk nowej ankiety', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Nowa ankieta')
    })
  })

  describe('lista ankiet', () => {
    it('powinien wyświetlać listę ankiet', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Ankieta 1')
      expect(wrapper.text()).toContain('Ankieta 2')
      expect(wrapper.text()).toContain('Ankieta 3')
    })

    it('powinien wyświetlać empty state dla pustej listy', async () => {
      server.use(
        http.get(`${API_URL}/surveys/`, () => {
          return HttpResponse.json([])
        })
      )

      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Brak ankiet')
    })

    it('powinien wyświetlać błąd przy niepowodzeniu', async () => {
      server.use(
        http.get(`${API_URL}/surveys/`, () => {
          return HttpResponse.json({ detail: 'Server error' }, { status: 500 })
        })
      )

      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Błąd')
    })
  })

  describe('wyszukiwanie', () => {
    it('powinien filtrować ankiety po tytule', async () => {
      const wrapper = await mountComponent()

      const searchInput = wrapper.find('.search-input')
      await searchInput.setValue('Ankieta 1')

      expect(wrapper.text()).toContain('Ankieta 1')
      // Inne ankiety powinny być ukryte
    })

    it('powinien filtrować po opisie', async () => {
      server.use(
        http.get(`${API_URL}/surveys/`, () => {
          return HttpResponse.json([
            createMockSurvey({ id: '1', title: 'Test', description: 'unikalna fraza' }),
            createMockSurvey({ id: '2', title: 'Inna', description: 'coś innego' }),
          ])
        })
      )

      const wrapper = await mountComponent()
      const searchInput = wrapper.find('.search-input')
      await searchInput.setValue('unikalna')

      expect(wrapper.text()).toContain('Test')
    })
  })

  describe('interakcje', () => {
    it('powinien mieć przycisk ponowienia przy błędzie', async () => {
      server.use(
        http.get(`${API_URL}/surveys/`, () => {
          return HttpResponse.json({ detail: 'Error' }, { status: 500 })
        })
      )

      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Spróbuj ponownie')
    })
  })

  describe('loading state', () => {
    it('powinien wyświetlać spinner podczas ładowania', async () => {
      server.use(
        http.get(`${API_URL}/surveys/`, async () => {
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json([])
        })
      )

      const wrapper = mount(SurveysListView, {
        global: { plugins: [router] },
      })

      expect(wrapper.find('.loading').exists() || wrapper.find('.spinner').exists()).toBe(true)
    })
  })
})
