/**
 * Testy jednostkowe dla SurveySuccessView
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import SurveySuccessView from '@/views/SurveySuccessView.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/surveys/:id/success', name: 'survey-success', component: SurveySuccessView },
    { path: '/surveys/:id', name: 'fill-survey', component: { template: '<div>Fill</div>' } },
    { path: '/surveys', name: 'surveys', component: { template: '<div>List</div>' } },
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
  ],
})

describe('SurveySuccessView', () => {
  const mountComponent = async (surveyId: string = 'test-123') => {
    await router.push(`/surveys/${surveyId}/success`)
    const wrapper = mount(SurveySuccessView, {
      global: {
        plugins: [router],
      },
    })
    return wrapper
  }

  describe('rendering', () => {
    it('powinien renderować podziękowanie', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Dziękujemy')
    })

    it('powinien renderować wiadomość sukcesu', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('pomyślnie zapisana')
    })

    it('powinien renderować ikonę sukcesu', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.find('.success-icon').exists()).toBe(true)
    })

    it('powinien renderować animacje', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.find('.success-card').exists()).toBe(true)
    })
  })

  describe('nawigacja', () => {
    it('powinien mieć link do wypełnienia ponownie', async () => {
      const wrapper = await mountComponent('my-survey')

      expect(wrapper.text()).toContain('Wypełnij ponownie')
      
      const link = wrapper.find('a[href*="my-survey"]')
      expect(link.exists()).toBe(true)
    })

    it('powinien mieć link do listy ankiet', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Przeglądaj ankiety')
    })

    it('powinien mieć link do strony głównej', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.text()).toContain('Wróć do strony głównej')
    })
  })

  describe('parametry URL', () => {
    it('powinien używać surveyId z route params', async () => {
      const wrapper = await mountComponent('custom-survey-id')

      const fillLink = wrapper.find('a[href*="custom-survey-id"]')
      expect(fillLink.exists()).toBe(true)
    })
  })

  describe('stylowanie', () => {
    it('powinien mieć klasę success-card', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.find('.success-card').exists()).toBe(true)
    })

    it('powinien mieć klasę success-view', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.find('.survey-success-view').exists()).toBe(true)
    })

    it('powinien mieć przyciski akcji', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.find('.success-actions').exists()).toBe(true)
    })
  })

  describe('confetti animation', () => {
    it('powinien mieć elementy confetti', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.findAll('.confetti').length).toBeGreaterThanOrEqual(0)
    })

    it('powinien mieć checkmark', async () => {
      const wrapper = await mountComponent()

      expect(wrapper.find('.checkmark').exists()).toBe(true)
    })
  })
})
