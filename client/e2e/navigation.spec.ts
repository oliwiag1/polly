/**
 * Testy E2E Playwright - Nawigacja i przepływy użytkownika
 */
import { test, expect } from '@playwright/test'

test.describe('Nawigacja główna', () => {
  test('powinna nawigować między wszystkimi stronami', async ({ page }) => {
    // Start na stronie głównej
    await page.goto('/')
    await expect(page).toHaveURL('/')
    
    // Do listy ankiet
    await page.getByRole('link', { name: /przeglądaj ankiety/i }).click()
    await expect(page).toHaveURL(/.*\/surveys/)
    
    // Do tworzenia ankiety
    await page.getByRole('main').getByRole('link', { name: /nowa ankieta/i }).click()
    await expect(page).toHaveURL(/.*\/surveys\/create/)
    
    // Wróć do strony głównej przez logo/home
    const homeLink = page.getByRole('navigation').getByRole('link', { name: /strona główna/i })
    await homeLink.click()
    await expect(page).toHaveURL('/')
  })

  test('powinna zachować historię przeglądarki', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('link', { name: /przeglądaj ankiety/i }).click()
    await expect(page).toHaveURL(/.*\/surveys/)
    
    await page.getByRole('navigation').getByRole('link', { name: /strona główna/i }).click()
    await expect(page).toHaveURL('/')
    
    // Wróć
    await page.goBack()
    await expect(page).toHaveURL(/.*\/surveys/)
  })
})

test.describe('Responsywność', () => {
  test('powinna działać na urządzeniach mobilnych', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')
    
    // Sprawdź czy strona jest widoczna
    await expect(page.locator('body')).toBeVisible()
    
    // Przyciski powinny być widoczne
    const createBtn = page.getByRole('link', { name: /utwórz ankietę/i })
    await expect(createBtn).toBeVisible()
  })

  test('powinna działać na tabletach', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.goto('/')
    
    await expect(page.locator('body')).toBeVisible()
  })

  test('powinna działać na desktopie', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 })
    await page.goto('/')
    
    await expect(page.locator('body')).toBeVisible()
  })
})

test.describe('Dostępność', () => {
  test('powinna mieć prawidłową strukturę nagłówków', async ({ page }) => {
    await page.goto('/')
    
    // Sprawdź czy jest h1
    const h1Count = await page.locator('h1').count()
    expect(h1Count).toBeGreaterThanOrEqual(1)
  })

  test('linki powinny być fokusowalne', async ({ page }) => {
    await page.goto('/')
    
    // Tab do pierwszego linku
    await page.keyboard.press('Tab')
    
    // Sprawdź czy jakiś element ma fokus
    const focusedElement = page.locator(':focus')
    await expect(focusedElement).toBeVisible()
  })

  test('formularze powinny mieć etykiety', async ({ page }) => {
    await page.goto('/surveys/create')
    
    // Sprawdź czy inputy mają powiązane labels
    const titleLabel = page.getByLabel(/tytuł/i)
    await expect(titleLabel).toBeVisible()
  })
})

test.describe('Obsługa błędów', () => {
  test('powinna obsłużyć nieznane ścieżki', async ({ page }) => {
    await page.goto('/nieistniejaca-strona-xyz')
    
    // Vue router powinien albo pokazać 404 albo obsłużyć to jakoś
    // Sprawdzamy że strona się załadowała i nie jest pusta
    await expect(page.locator('body')).toBeVisible()
    
    // Albo mamy błąd, albo jesteśmy na stronie (catchall)
    const hasContent = await page.locator('h1, h2, .error, .not-found, main').first().isVisible()
    expect(hasContent).toBeTruthy()
  })
})

test.describe('Wydajność', () => {
  test('strona główna powinna załadować się szybko', async ({ page }) => {
    const startTime = Date.now()
    await page.goto('/')
    await page.waitForLoadState('domcontentloaded')
    const loadTime = Date.now() - startTime
    
    // Strona powinna załadować się w mniej niż 5 sekund
    expect(loadTime).toBeLessThan(5000)
  })
})
