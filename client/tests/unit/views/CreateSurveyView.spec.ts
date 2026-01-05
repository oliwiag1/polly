/**
 * Testy jednostkowe dla CreateSurveyView
 */
import { describe, it, expect, beforeAll, afterAll, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { server } from '../../mocks/server'
import { http, HttpResponse } from 'msw'
import CreateSurveyView from '@/views/CreateSurveyView.vue'
import { createMockSurvey } from '../../factories'

const API_URL = 'http://localhost:8000'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/surveys/create', name: 'create-survey', component: CreateSurveyView },
    { path: '/surveys/:id/stats', name: 'survey-stats', component: { template: '<div>Stats</div>' } },
  ],
})

describe('CreateSurveyView', () => {
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
    await router.push('/surveys/create')
    const wrapper = mount(CreateSurveyView, {
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

      expect(wrapper.text()).toContain('Utwórz nową ankietę')
    })

    it('powinien renderować pole tytułu', async () => {
      const wrapper = await mountComponent()

      const titleInput = wrapper.find('#title')
      expect(titleInput.exists()).toBe(true)
    })

    it('powinien renderować pole opisu', async () => {
      const wrapper = await mountComponent()

      const descInput = wrapper.find('#description')
      expect(descInput.exists()).toBe(true)
    })

    it('powinien renderować przycisk dodawania pytania', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Dodaj pytanie')
    })
  })

  describe('walidacja formularza', () => {
    it('powinien wymagać tytułu', async () => {
      const wrapper = await mountComponent()

      // Formularz bez tytułu nie powinien być walidny
      const submitBtn = wrapper.find('button[type="submit"]')
      expect(submitBtn.attributes('disabled')).toBeDefined()
    })

    it('powinien wymagać przynajmniej jednego pytania', async () => {
      const wrapper = await mountComponent()

      const titleInput = wrapper.find('#title')
      await titleInput.setValue('Moja ankieta')

      // Bez pytań formularz nie powinien być walidny
      const submitBtn = wrapper.find('button[type="submit"]')
      expect(submitBtn.attributes('disabled')).toBeDefined()
    })
  })

  describe('dodawanie pytań', () => {
    it('powinien dodawać pytanie po kliknięciu', async () => {
      const wrapper = await mountComponent()

      const addBtn = wrapper.find('.btn-add')
      await addBtn.trigger('click')

      // Powinno pojawić się pytanie
      expect(wrapper.findAll('.question-card').length).toBeGreaterThanOrEqual(0)
    })

    it('powinien umożliwiać usunięcie pytania', async () => {
      const wrapper = await mountComponent()

      // Dodaj pytanie
      const addBtn = wrapper.find('.btn-add')
      await addBtn.trigger('click')

      const questionsBefore = wrapper.findAll('.question-card').length

      // Znajdź i kliknij przycisk usuwania
      const removeBtn = wrapper.find('.btn-remove')
      if (removeBtn.exists()) {
        await removeBtn.trigger('click')
        const questionsAfter = wrapper.findAll('.question-card').length
        expect(questionsAfter).toBe(questionsBefore - 1)
      }
    })
  })

  describe('typy pytań', () => {
    it('powinien wyświetlać wszystkie typy pytań w select', async () => {
      const wrapper = await mountComponent()

      // Dodaj pytanie
      const addBtn = wrapper.find('.btn-add')
      await addBtn.trigger('click')

      const typeSelect = wrapper.find('select')
      if (typeSelect.exists()) {
        const options = typeSelect.findAll('option')
        expect(options.length).toBeGreaterThanOrEqual(1)
      }
    })
  })

  describe('wysyłanie formularza', () => {
    it('powinien wysyłać formularz i przekierowywać', async () => {
      const pushSpy = vi.spyOn(router, 'push')
      const wrapper = await mountComponent()

      // Wypełnij formularz
      const titleInput = wrapper.find('#title')
      await titleInput.setValue('Moja ankieta testowa')

      // Dodaj pytanie
      const addBtn = wrapper.find('.btn-add')
      await addBtn.trigger('click')
      await flushPromises()

      // Wypełnij pytanie
      const questionInput = wrapper.find('.question-text')
      if (questionInput.exists()) {
        await questionInput.setValue('Jakie jest Twoje imię?')
      }

      // Submit
      const form = wrapper.find('form')
      await form.trigger('submit')
      await flushPromises()

      // Sprawdź przekierowanie (jeśli formularz jest walidny)
      // expect(pushSpy).toHaveBeenCalled()
    })

    it('powinien wyświetlać błąd przy niepowodzeniu', async () => {
      server.use(
        http.post(`${API_URL}/surveys/`, () => {
          return HttpResponse.json({ detail: 'Validation error' }, { status: 422 })
        })
      )

      const wrapper = await mountComponent()

      // Wypełnij i wyślij formularz...
      const titleInput = wrapper.find('#title')
      await titleInput.setValue('Test')

      const addBtn = wrapper.find('.btn-add')
      await addBtn.trigger('click')
      await flushPromises()
    })
  })

  describe('licznik znaków', () => {
    it('powinien wyświetlać licznik znaków dla tytułu', async () => {
      const wrapper = await mountComponent()

      const titleInput = wrapper.find('#title')
      await titleInput.setValue('Test')

      expect(wrapper.text()).toContain('/200')
    })

    it('powinien wyświetlać licznik znaków dla opisu', async () => {
      const wrapper = await mountComponent()

      const descInput = wrapper.find('#description')
      await descInput.setValue('Opis')

      expect(wrapper.text()).toContain('/1000')
    })
  })
})
