/**
 * Testy E2E Playwright - Strona główna
 */
import { test, expect } from '@playwright/test'

test.describe('Strona główna', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('powinna wyświetlać logo i tytuł Polly', async ({ page }) => {
    await expect(page.locator('h1, .logo')).toContainText(/Polly/i)
  })

  test('powinna mieć przycisk "Utwórz ankietę"', async ({ page }) => {
    const createBtn = page.getByRole('link', { name: /utwórz ankietę/i })
    await expect(createBtn).toBeVisible()
  })

  test('powinna mieć przycisk "Przeglądaj ankiety"', async ({ page }) => {
    const browseBtn = page.getByRole('link', { name: /przeglądaj ankiety/i })
    await expect(browseBtn).toBeVisible()
  })

  test('powinna wyświetlać status backendu', async ({ page }) => {
    await expect(page.getByText(/status backendu/i)).toBeVisible()
  })

  test('powinna nawigować do tworzenia ankiety', async ({ page }) => {
    await page.getByRole('link', { name: /utwórz ankietę/i }).click()
    await expect(page).toHaveURL(/.*\/surveys\/create/)
  })

  test('powinna nawigować do listy ankiet', async ({ page }) => {
    await page.getByRole('link', { name: /przeglądaj ankiety/i }).click()
    await expect(page).toHaveURL(/.*\/surveys/)
  })
})
