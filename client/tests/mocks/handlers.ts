/**
 * Mock handlers dla MSW (Mock Service Worker)
 */
import { http, HttpResponse } from 'msw'
import { 
  createMockSurvey, 
  createMockSurveyStats, 
  createMockHealthStatus, 
  createMockApiInfo,
  createMockSurveyResponse,
} from '../factories'

const API_URL = 'http://localhost:8000'

export const handlers = [
  // Health & Info
  http.get(`${API_URL}/health`, () => {
    return HttpResponse.json(createMockHealthStatus())
  }),

  http.get(`${API_URL}/`, () => {
    return HttpResponse.json(createMockApiInfo())
  }),

  // Surveys - List
  http.get(`${API_URL}/surveys/`, () => {
    return HttpResponse.json([
      createMockSurvey({ id: 'survey-1', title: 'Ankieta 1' }),
      createMockSurvey({ id: 'survey-2', title: 'Ankieta 2' }),
      createMockSurvey({ id: 'survey-3', title: 'Ankieta 3' }),
    ])
  }),

  // Surveys - Get by ID
  http.get(`${API_URL}/surveys/:id`, ({ params }) => {
    const { id } = params
    if (id === 'not-found') {
      return HttpResponse.json(
        { detail: 'Survey not found' },
        { status: 404 }
      )
    }
    return HttpResponse.json(createMockSurvey({ id: id as string }))
  }),

  // Surveys - Create
  http.post(`${API_URL}/surveys/`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>
    return HttpResponse.json(
      createMockSurvey({ 
        id: 'new-survey-123',
        title: body.title as string,
        description: body.description as string | null,
      }),
      { status: 201 }
    )
  }),

  // Responses - Submit
  http.post(`${API_URL}/surveys/:id/responses`, ({ params }) => {
    const { id } = params
    if (id === 'error-survey') {
      return HttpResponse.json(
        { detail: 'Required question was not answered' },
        { status: 400 }
      )
    }
    return HttpResponse.json(
      createMockSurveyResponse({ survey_id: id as string }),
      { status: 201 }
    )
  }),

  // Stats
  http.get(`${API_URL}/surveys/:id/stats`, ({ params }) => {
    const { id } = params
    if (id === 'not-found') {
      return HttpResponse.json(
        { detail: 'Survey not found' },
        { status: 404 }
      )
    }
    return HttpResponse.json(createMockSurveyStats({ survey_id: id as string }))
  }),
]

// Handlers dla błędów
export const errorHandlers = [
  http.get(`${API_URL}/health`, () => {
    return HttpResponse.json(
      { detail: 'Service unavailable' },
      { status: 503 }
    )
  }),

  http.get(`${API_URL}/`, () => {
    return HttpResponse.json(
      { detail: 'Service unavailable' },
      { status: 503 }
    )
  }),

  http.get(`${API_URL}/surveys/`, () => {
    return HttpResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    )
  }),
]
