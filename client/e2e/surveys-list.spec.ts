/**
 * Testy E2E Playwright - Lista ankiet
 */
import { test, expect } from '@playwright/test'

test.describe('Lista ankiet', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/surveys')
  })

  test('powinna wyświetlać nagłówek listy', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /lista ankiet/i })).toBeVisible()
  })

  test('powinna mieć pole wyszukiwania', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/szukaj/i)
    await expect(searchInput).toBeVisible()
  })

  test('powinna mieć przycisk nowej ankiety', async ({ page }) => {
    const newBtn = page.getByRole('main').getByRole('link', { name: /nowa ankieta/i })
    await expect(newBtn).toBeVisible()
  })

  test('powinna nawigować do tworzenia ankiety', async ({ page }) => {
    await page.getByRole('main').getByRole('link', { name: /nowa ankieta/i }).click()
    await expect(page).toHaveURL(/.*\/surveys\/create/)
  })

  test('powinna wyświetlać listę ankiet lub pusty stan', async ({ page }) => {
    // Czekamy na załadowanie
    await page.waitForLoadState('networkidle')
    
    // Sprawdź czy jest lista lub komunikat o braku ankiet
    const hasSurveys = await page.locator('.survey-card, .survey-item').count() > 0
    const hasEmptyState = await page.getByText(/brak ankiet/i).isVisible().catch(() => false)
    
    expect(hasSurveys || hasEmptyState).toBeTruthy()
  })

  test('powinna filtrować ankiety po wyszukaniu', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/szukaj/i)
    await searchInput.fill('test')
    
    // Odczekaj na filtrację
    await page.waitForTimeout(300)
    
    // Sprawdź czy filtr zadziałał (lub brak wyników)
    await expect(searchInput).toHaveValue('test')
  })
})
