/**
 * Testy jednostkowe dla HomeView
 */
import { describe, it, expect, beforeAll, afterAll, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { server } from '../../mocks/server'
import { http, HttpResponse } from 'msw'
import HomeView from '@/views/HomeView.vue'
import { createMockHealthStatus, createMockApiInfo } from '../../factories'

const API_URL = 'http://localhost:8000'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/surveys', name: 'surveys', component: { template: '<div>Surveys</div>' } },
    { path: '/surveys/create', name: 'create-survey', component: { template: '<div>Create</div>' } },
  ],
})

describe('HomeView', () => {
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
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
      },
    })
    await flushPromises()
    return wrapper
  }

  describe('rendering', () => {
    it('powinien renderować tytuł', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Polly')
    })

    it('powinien renderować przyciski nawigacji', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Utwórz ankietę')
      expect(wrapper.text()).toContain('Przeglądaj ankiety')
    })

    it('powinien wyświetlać status backendu', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Status backendu')
    })
  })

  describe('health status', () => {
    it('powinien wyświetlać status healthy', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('HEALTHY')
    })

    it('powinien wyświetlać informacje o API', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Polly Survey API')
      expect(wrapper.text()).toContain('1.0.0')
    })

    it('powinien wyświetlać błąd przy niepowodzeniu', async () => {
      server.use(
        http.get(`${API_URL}/health`, () => {
          return HttpResponse.json({ detail: 'Connection failed' }, { status: 503 })
        }),
        http.get(`${API_URL}/`, () => {
          return HttpResponse.json({ detail: 'Connection failed' }, { status: 503 })
        })
      )

      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Błąd połączenia')
    })
  })

  describe('interactions', () => {
    it('powinien mieć przycisk odświeżania', async () => {
      const wrapper = await mountComponent()

      const refreshBtn = wrapper.find('.refresh-btn')
      expect(refreshBtn.exists()).toBe(true)
    })

    it('powinien odświeżać status po kliknięciu', async () => {
      const wrapper = await mountComponent()

      const refreshBtn = wrapper.find('.refresh-btn')
      await refreshBtn.trigger('click')
      await flushPromises()

      expect(wrapper.text()).toContain('HEALTHY')
    })
  })

  describe('loading state', () => {
    it('powinien wyświetlać spinner podczas ładowania', async () => {
      server.use(
        http.get(`${API_URL}/health`, async () => {
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json(createMockHealthStatus())
        }),
        http.get(`${API_URL}/`, async () => {
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json(createMockApiInfo())
        })
      )

      const wrapper = mount(HomeView, {
        global: { plugins: [router] },
      })

      expect(wrapper.find('.loading').exists() || wrapper.find('.spinner').exists()).toBe(true)
    })
  })
})
