/**
 * Testy jednostkowe dla routera Vue
 */
import { describe, it, expect } from 'vitest'
import router from '@/router'

describe('Router', () => {
  describe('routes configuration', () => {
    it('powinien mieć zdefiniowane wszystkie ścieżki', () => {
      const routes = router.getRoutes()
      const paths = routes.map(r => r.path)

      expect(paths).toContain('/')
      expect(paths).toContain('/surveys')
      expect(paths).toContain('/surveys/create')
      expect(paths).toContain('/surveys/:id')
      expect(paths).toContain('/surveys/:id/stats')
      expect(paths).toContain('/surveys/:id/success')
    })

    it('powinien mieć poprawne nazwy ścieżek', () => {
      const routes = router.getRoutes()
      const names = routes.map(r => r.name)

      expect(names).toContain('home')
      expect(names).toContain('surveys')
      expect(names).toContain('create-survey')
      expect(names).toContain('fill-survey')
      expect(names).toContain('survey-stats')
      expect(names).toContain('survey-success')
    })

    it('powinien mieć 6 ścieżek', () => {
      const routes = router.getRoutes()

      expect(routes).toHaveLength(6)
    })
  })

  describe('route matching', () => {
    it('powinien dopasować ścieżkę główną', () => {
      const resolved = router.resolve('/')

      expect(resolved.name).toBe('home')
    })

    it('powinien dopasować listę ankiet', () => {
      const resolved = router.resolve('/surveys')

      expect(resolved.name).toBe('surveys')
    })

    it('powinien dopasować tworzenie ankiety', () => {
      const resolved = router.resolve('/surveys/create')

      expect(resolved.name).toBe('create-survey')
    })

    it('powinien dopasować wypełnianie ankiety z parametrem', () => {
      const resolved = router.resolve('/surveys/123')

      expect(resolved.name).toBe('fill-survey')
      expect(resolved.params.id).toBe('123')
    })

    it('powinien dopasować statystyki ankiety z parametrem', () => {
      const resolved = router.resolve('/surveys/abc-123/stats')

      expect(resolved.name).toBe('survey-stats')
      expect(resolved.params.id).toBe('abc-123')
    })

    it('powinien dopasować sukces z parametrem', () => {
      const resolved = router.resolve('/surveys/xyz/success')

      expect(resolved.name).toBe('survey-success')
      expect(resolved.params.id).toBe('xyz')
    })
  })

  describe('route generation', () => {
    it('powinien generować poprawne linki', () => {
      expect(router.resolve({ name: 'home' }).href).toBe('/')
      expect(router.resolve({ name: 'surveys' }).href).toBe('/surveys')
      expect(router.resolve({ name: 'create-survey' }).href).toBe('/surveys/create')
    })

    it('powinien generować linki z parametrami', () => {
      const fillUrl = router.resolve({ 
        name: 'fill-survey', 
        params: { id: 'test-123' } 
      }).href

      expect(fillUrl).toBe('/surveys/test-123')

      const statsUrl = router.resolve({ 
        name: 'survey-stats', 
        params: { id: 'test-123' } 
      }).href

      expect(statsUrl).toBe('/surveys/test-123/stats')
    })
  })

  describe('history mode', () => {
    it('powinien używać web history', () => {
      expect(router.options.history).toBeDefined()
    })
  })
})
