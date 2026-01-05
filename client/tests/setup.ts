/**
 * Setup dla testów Vitest
 */
import { vi } from 'vitest'

// Mock dla import.meta.env
vi.stubGlobal('import.meta', {
  env: {
    VITE_API_URL: 'http://localhost:8000',
    BASE_URL: '/',
  },
})

// Mock dla navigator.clipboard - użyj defineProperty
const writeTextMock = vi.fn().mockResolvedValue(undefined)
const readTextMock = vi.fn().mockResolvedValue('')

Object.defineProperty(navigator, 'clipboard', {
  value: {
    writeText: writeTextMock,
    readText: readTextMock,
  },
  writable: true,
  configurable: true,
})

// Mock dla window.alert
vi.stubGlobal('alert', vi.fn())

// Mock dla console.error (aby nie zaśmiecać output testów)
vi.spyOn(console, 'error').mockImplementation(() => {})
