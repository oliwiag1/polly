/**
 * Testy E2E Playwright - Wypełnianie ankiety
 */
import { test, expect } from '@playwright/test'

test.describe('Wypełnianie ankiety', () => {
  // Te testy wymagają istniejącej ankiety w bazie
  // Używamy ID przykładowej ankiety lub najpierw ją tworzymy
  
  test('powinna wyświetlać błąd dla nieistniejącej ankiety', async ({ page }) => {
    await page.goto('/surveys/nieistniejace-id-12345')
    
    // Czekaj na załadowanie
    await page.waitForLoadState('networkidle')
    
    // Powinna być wiadomość o błędzie
    const hasError = await page.getByText(/błąd|nie znaleziono|not found/i).isVisible()
    expect(hasError).toBeTruthy()
  })

  test('powinna mieć przycisk powrotu przy błędzie', async ({ page }) => {
    await page.goto('/surveys/nieistniejace-id-12345')
    await page.waitForLoadState('networkidle')
    
    const backBtn = page.getByRole('link', { name: /wróć|powrót|lista/i })
    await expect(backBtn).toBeVisible()
  })
})

test.describe('Przepływ wypełniania ankiety', () => {
  test('powinna wyświetlać formularz ankiety dla istniejącej', async ({ page }) => {
    // Najpierw idź do listy i znajdź ankietę
    await page.goto('/surveys')
    await page.waitForLoadState('networkidle')
    
    // Sprawdź czy są ankiety
    const surveyCards = page.locator('.survey-card, .survey-item, a[href*="/surveys/"]')
    const count = await surveyCards.count()
    
    if (count > 0) {
      // Kliknij pierwszą ankietę
      const firstSurvey = surveyCards.first()
      await firstSurvey.click()
      
      // Powinna być na stronie ankiety
      await page.waitForLoadState('networkidle')
      
      // Sprawdź czy widoczny jest formularz lub tytuł
      const hasContent = await page.locator('h1, h2, .survey-title').first().isVisible()
      expect(hasContent).toBeTruthy()
    } else {
      // Brak ankiet - to też jest poprawne
      test.skip()
    }
  })
})
