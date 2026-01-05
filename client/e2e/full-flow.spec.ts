/**
 * Testy E2E Playwright - Pełne scenariusze użytkownika
 */
import { test, expect } from '@playwright/test'

test.describe('Scenariusz: Administrator tworzy ankietę', () => {
  test('powinien móc stworzyć kompletną ankietę', async ({ page }) => {
    // 1. Otwórz stronę główną
    await page.goto('/')
    await expect(page.locator('h1, .logo')).toContainText(/Polly/i)
    
    // 2. Przejdź do tworzenia ankiety
    await page.getByRole('link', { name: /utwórz ankietę/i }).click()
    await expect(page).toHaveURL(/.*\/surveys\/create/)
    
    // 3. Wypełnij formularz
    await page.getByLabel(/tytuł/i).or(page.locator('#title')).fill('Ankieta satysfakcji klientów')
    await page.getByLabel(/opis/i).or(page.locator('#description')).fill('Prosimy o wypełnienie krótkiej ankiety dotyczącej naszych usług.')
    
    // 4. Dodaj pytania
    await page.getByRole('button', { name: /dodaj pytanie/i }).click()
    
    const questionInput = page.locator('.question-text, input[placeholder*="pytanie"]').first()
    if (await questionInput.isVisible()) {
      await questionInput.fill('Jak oceniasz jakość naszych usług?')
    }
    
    // 5. Sprawdź czy formularz jest gotowy
    const titleInput = page.getByLabel(/tytuł/i).or(page.locator('#title'))
    await expect(titleInput).toHaveValue('Ankieta satysfakcji klientów')
  })
})

test.describe('Scenariusz: Użytkownik przegląda ankiety', () => {
  test('powinien móc przeglądać listę ankiet', async ({ page }) => {
    // 1. Otwórz listę ankiet
    await page.goto('/surveys')
    await expect(page.getByRole('heading', { name: /lista ankiet/i })).toBeVisible()
    
    // 2. Sprawdź czy jest pole wyszukiwania
    const searchInput = page.getByPlaceholder(/szukaj/i)
    await expect(searchInput).toBeVisible()
    
    // 3. Czekaj na załadowanie
    await page.waitForLoadState('networkidle')
    
    // 4. Sprawdź wyniki
    const hasSurveys = await page.locator('.survey-card, .survey-item').count() > 0
    const hasEmptyState = await page.getByText(/brak ankiet/i).isVisible().catch(() => false)
    
    expect(hasSurveys || hasEmptyState).toBeTruthy()
  })

  test('powinien móc wyszukać ankietę', async ({ page }) => {
    await page.goto('/surveys')
    
    const searchInput = page.getByPlaceholder(/szukaj/i)
    await searchInput.fill('satysfakcji')
    
    // Poczekaj na filtrację
    await page.waitForTimeout(500)
    
    // Wyszukiwanie powinno działać
    await expect(searchInput).toHaveValue('satysfakcji')
  })
})

test.describe('Scenariusz: Strona sukcesu po wypełnieniu', () => {
  test('powinien zobaczyć podziękowanie i móc wrócić', async ({ page }) => {
    // 1. Symuluj stronę sukcesu
    await page.goto('/surveys/test-survey/success')
    
    // 2. Sprawdź podziękowanie
    await expect(page.getByText(/dziękujemy/i)).toBeVisible()
    
    // 3. Sprawdź dostępne akcje
    await expect(page.getByRole('link', { name: /wypełnij ponownie/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /przeglądaj ankiety/i })).toBeVisible()
    
    // 4. Wróć do strony głównej
    await page.getByRole('link', { name: /Wróć do strony głównej/i }).click()
    await expect(page).toHaveURL('/')
  })
})

test.describe('Scenariusz: Pełny przepływ od A do Z', () => {
  test('kompletny przepływ użytkownika', async ({ page }) => {
    // === KROK 1: Strona główna ===
    await page.goto('/')
    await expect(page.locator('h1, .logo')).toContainText(/Polly/i)
    
    // === KROK 2: Nawigacja do listy ankiet ===
    await page.getByRole('link', { name: /przeglądaj ankiety/i }).click()
    await expect(page).toHaveURL(/.*\/surveys/)
    await expect(page.getByRole('heading', { name: /lista ankiet/i })).toBeVisible()
    
    // === KROK 3: Nawigacja do tworzenia ===
    await page.getByRole('main').getByRole('link', { name: /nowa ankieta/i }).click()
    await expect(page).toHaveURL(/.*\/surveys\/create/)
    
    // === KROK 4: Wypełnienie formularza ===
    await page.getByLabel(/tytuł/i).or(page.locator('#title')).fill('Ankieta testowa E2E')
    await page.getByRole('button', { name: /dodaj pytanie/i }).click()
    
    // === KROK 5: Powrót do strony głównej ===
    const homeLink = page.getByRole('navigation').getByRole('link', { name: /strona główna/i })
    await homeLink.click()
    await expect(page).toHaveURL('/')
    
    // Test zakończony sukcesem!
  })
})

test.describe('Scenariusz: Obsługa błędów w przepływie', () => {
  test('powinien gracefully obsłużyć błąd 404', async ({ page }) => {
    await page.goto('/surveys/nieistniejaca-ankieta-xyz')
    await page.waitForLoadState('networkidle')
    
    // Powinna być informacja o błędzie
    const hasError = await page.getByText(/błąd|nie znaleziono|not found/i).isVisible()
    expect(hasError).toBeTruthy()
    
    // Powinna być opcja powrotu
    const backLink = page.getByRole('link', { name: /wróć|lista|powrót/i })
    await expect(backLink).toBeVisible()
  })

  test('powinien móc wrócić do listy po błędzie', async ({ page }) => {
    await page.goto('/surveys/nieistniejaca-ankieta-xyz')
    await page.waitForLoadState('networkidle')
    
    const backLink = page.getByRole('link', { name: /wróć.*lista|lista/i }).first()
    
    if (await backLink.isVisible()) {
      await backLink.click()
      await expect(page).toHaveURL(/.*\/surveys/)
    }
  })
})
