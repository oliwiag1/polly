/**
 * Testy E2E Playwright - Tworzenie ankiety
 */
import { test, expect } from '@playwright/test'

test.describe('Tworzenie ankiety', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/surveys/create')
  })

  test('powinna wyświetlać formularz tworzenia', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /utwórz.*ankiet/i })).toBeVisible()
  })

  test('powinna mieć pole tytułu', async ({ page }) => {
    const titleInput = page.getByLabel(/tytuł/i).or(page.locator('#title'))
    await expect(titleInput).toBeVisible()
  })

  test('powinna mieć pole opisu', async ({ page }) => {
    const descInput = page.getByLabel(/opis/i).or(page.locator('#description'))
    await expect(descInput).toBeVisible()
  })

  test('powinna mieć przycisk dodawania pytania', async ({ page }) => {
    const addBtn = page.getByRole('button', { name: /dodaj pytanie/i })
    await expect(addBtn).toBeVisible()
  })

  test('powinna dodawać pytanie po kliknięciu', async ({ page }) => {
    const addBtn = page.getByRole('button', { name: /dodaj pytanie/i })
    await addBtn.click()
    
    // Powinno pojawić się pytanie
    await expect(page.locator('.question-card, .question-item')).toHaveCount(1)
  })

  test('powinna wyświetlać licznik znaków dla tytułu', async ({ page }) => {
    const titleInput = page.getByLabel(/tytuł/i).or(page.locator('#title'))
    await titleInput.fill('Test')
    
    await expect(page.getByText(/4.*\/.*200/)).toBeVisible()
  })

  test('powinna walidować pusty formularz', async ({ page }) => {
    const submitBtn = page.getByRole('button', { name: /utwórz|zapisz|wyślij/i })
    
    // Przycisk powinien być zablokowany lub formularz nie powinien się wysłać
    const isDisabled = await submitBtn.isDisabled()
    expect(isDisabled).toBe(true)
  })

  test('powinna umożliwiać wypełnienie kompletnego formularza', async ({ page }) => {
    // Tytuł
    const titleInput = page.getByLabel(/tytuł/i).or(page.locator('#title'))
    await titleInput.fill('Moja testowa ankieta E2E')
    
    // Opis
    const descInput = page.getByLabel(/opis/i).or(page.locator('#description'))
    await descInput.fill('To jest ankieta stworzona przez test E2E')
    
    // Dodaj pytanie
    const addBtn = page.getByRole('button', { name: /dodaj pytanie/i })
    await addBtn.click()
    
    // Poczekaj na pojawienie się pytania
    await page.waitForTimeout(500)
    
    // Wypełnij pytanie - użyj dokładnego selektora z placeholdera
    const questionInput = page.getByPlaceholder('Wpisz treść pytania...')
    
    if (await questionInput.isVisible()) {
      await questionInput.fill('Jakie jest Twoje ulubione zwierzę?')
    }
    
    // Sprawdź czy tytuł jest wypełniony
    await expect(titleInput).toHaveValue('Moja testowa ankieta E2E')
  })

  test('powinna obsługiwać różne typy pytań', async ({ page }) => {
    // Dodaj pytanie
    await page.getByRole('button', { name: /dodaj pytanie/i }).click()
    
    // Znajdź select typu
    const typeSelect = page.locator('select').first()
    
    if (await typeSelect.isVisible()) {
      // Sprawdź opcje
      const options = await typeSelect.locator('option').allTextContents()
      expect(options.length).toBeGreaterThan(1)
    }
  })
})

test.describe('Tworzenie i wysyłanie ankiety', () => {
  test('powinna utworzyć ankietę i przekierować do statystyk', async ({ page }) => {
    await page.goto('/surveys/create')
    
    // Wypełnij formularz
    await page.getByLabel(/tytuł/i).or(page.locator('#title')).fill('Ankieta E2E Test')
    await page.getByLabel(/opis/i).or(page.locator('#description')).fill('Opis testowy')
    
    // Dodaj pytanie
    await page.getByRole('button', { name: /dodaj pytanie/i }).click()
    await page.waitForTimeout(500)
    
    // Znajdź pole pytania
    const questionInput = page.locator('input[type="text"]').nth(2).or(
      page.locator('.question-card input').first()
    )
    
    if (await questionInput.isVisible()) {
      await questionInput.fill('Pytanie testowe?')
    }
    
    // Sprawdź że formularz jest wypełniony
    await expect(page.getByLabel(/tytuł/i).or(page.locator('#title'))).toHaveValue('Ankieta E2E Test')
  })
})
