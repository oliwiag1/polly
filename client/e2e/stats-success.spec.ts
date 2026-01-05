/**
 * Testy E2E Playwright - Statystyki ankiety
 */
import { test, expect } from '@playwright/test'

test.describe('Statystyki ankiety', () => {
  test('powinna wyświetlać błąd dla nieistniejącej ankiety', async ({ page }) => {
    await page.goto('/surveys/nieistniejace-id-stats/stats')
    
    await page.waitForLoadState('networkidle')
    
    const hasError = await page.getByText(/błąd|nie znaleziono|not found/i).isVisible()
    expect(hasError).toBeTruthy()
  })

  test('powinna mieć przycisk powrotu do listy', async ({ page }) => {
    await page.goto('/surveys/nieistniejace-id-stats/stats')
    await page.waitForLoadState('networkidle')
    
    const backBtn = page.getByRole('link', { name: /wróć|lista/i })
    await expect(backBtn).toBeVisible()
  })
})

test.describe('Strona sukcesu', () => {
  test('powinna wyświetlać podziękowanie', async ({ page }) => {
    await page.goto('/surveys/test-id/success')
    
    await expect(page.getByText(/dziękujemy/i)).toBeVisible()
  })

  test('powinna mieć link do wypełnienia ponownie', async ({ page }) => {
    await page.goto('/surveys/test-id/success')
    
    const refillLink = page.getByRole('link', { name: /wypełnij ponownie/i })
    await expect(refillLink).toBeVisible()
  })

  test('powinna mieć link do listy ankiet', async ({ page }) => {
    await page.goto('/surveys/test-id/success')
    
    const listLink = page.getByRole('link', { name: /przeglądaj ankiety/i })
    await expect(listLink).toBeVisible()
  })

  test('powinna mieć link do strony głównej', async ({ page }) => {
    await page.goto('/surveys/test-id/success')
    
    const homeLink = page.getByRole('main').getByRole('link', { name: /wróć do strony głównej/i })
    await expect(homeLink).toBeVisible()
  })

  test('powinna nawigować do strony głównej', async ({ page }) => {
    await page.goto('/surveys/test-id/success')
    
    await page.getByRole('link', { name: /Wróć do strony głównej/i }).click()
    await expect(page).toHaveURL('/')
  })
})
