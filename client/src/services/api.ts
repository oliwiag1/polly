import type {
  Survey,
  SurveyCreate,
  SurveyResponse,
  AnswerSubmit,
  SurveyStats,
  HealthStatus,
  ApiInfo
} from '@/types/survey'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers
      },
      ...options
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // Health & Info
  async getHealth(): Promise<HealthStatus> {
    return this.request<HealthStatus>('/health')
  }

  async getApiInfo(): Promise<ApiInfo> {
    return this.request<ApiInfo>('/')
  }

  // Surveys
  async getAllSurveys(): Promise<Survey[]> {
    return this.request<Survey[]>('/surveys/')
  }

  async getSurvey(id: string): Promise<Survey> {
    return this.request<Survey>(`/surveys/${id}`)
  }

  async createSurvey(survey: SurveyCreate): Promise<Survey> {
    return this.request<Survey>('/surveys/', {
      method: 'POST',
      body: JSON.stringify(survey)
    })
  }

  // Responses
  async submitResponse(surveyId: string, answers: AnswerSubmit): Promise<SurveyResponse> {
    return this.request<SurveyResponse>(`/surveys/${surveyId}/responses`, {
      method: 'POST',
      body: JSON.stringify(answers)
    })
  }

  // Statistics
  async getSurveyStats(surveyId: string): Promise<SurveyStats> {
    return this.request<SurveyStats>(`/surveys/${surveyId}/stats`)
  }
}

export const apiService = new ApiService()
export default apiService
