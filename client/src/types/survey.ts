// Typy danych dla ankiet

export enum QuestionType {
  TEXT = 'text',
  SINGLE_CHOICE = 'single_choice',
  MULTIPLE_CHOICE = 'multiple_choice',
  RATING = 'rating',
  YES_NO = 'yes_no'
}

export interface Question {
  id: string
  text: string
  type: QuestionType
  required: boolean
  options?: string[] | null
  min_rating?: number | null
  max_rating?: number | null
}

export interface SurveyLinks {
  survey_url: string
  stats_url: string
}

export interface Survey {
  id: string
  title: string
  description?: string | null
  questions: Question[]
  created_at: string
  links: SurveyLinks
}

export interface SurveyCreate {
  title: string
  description?: string | null
  questions: Question[]
}

export interface Answer {
  question_id: string
  value: string | string[] | number | boolean
}

export interface AnswerSubmit {
  answers: Answer[]
  respondent_id?: string | null
}

export interface SurveyResponse {
  id: string
  survey_id: string
  answers: Answer[]
  respondent_id?: string | null
  submitted_at: string
}

export interface QuestionStats {
  question_id: string
  question_text: string
  question_type: QuestionType
  total_responses: number
  answer_distribution: Record<string, number>
  average_value?: number | null
}

export interface SurveyStats {
  survey_id: string
  survey_title: string
  total_responses: number
  questions_stats: QuestionStats[]
  created_at: string
  last_response_at?: string | null
}

export interface HealthStatus {
  status: string
  database: {
    surveys: number
    responses: number
  }
}

export interface ApiInfo {
  name: string
  version: string
  docs: string
  redoc: string
}
