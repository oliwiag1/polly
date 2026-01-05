/**
 * Testy jednostkowe dla typów survey.ts
 */
import { describe, it, expect } from 'vitest'
import { QuestionType } from '@/types/survey'
import { 
  createMockQuestion, 
  createMockSurvey, 
  createMockSurveyStats,
  createMockAnswer,
  allQuestionTypes,
} from '../../factories'

describe('QuestionType Enum', () => {
  it('powinien mieć wszystkie typy pytań', () => {
    expect(QuestionType.TEXT).toBe('text')
    expect(QuestionType.SINGLE_CHOICE).toBe('single_choice')
    expect(QuestionType.MULTIPLE_CHOICE).toBe('multiple_choice')
    expect(QuestionType.RATING).toBe('rating')
    expect(QuestionType.YES_NO).toBe('yes_no')
  })

  it('powinien mieć dokładnie 5 typów', () => {
    const types = Object.values(QuestionType)
    expect(types).toHaveLength(5)
  })
})

describe('Question Interface', () => {
  it('powinien tworzyć pytanie tekstowe', () => {
    const question = createMockQuestion({
      id: 'q1',
      text: 'Jak masz na imię?',
      type: QuestionType.TEXT,
      required: true,
    })

    expect(question.id).toBe('q1')
    expect(question.text).toBe('Jak masz na imię?')
    expect(question.type).toBe(QuestionType.TEXT)
    expect(question.required).toBe(true)
    expect(question.options).toBeNull()
  })

  it('powinien tworzyć pytanie z opcjami wyboru', () => {
    const question = createMockQuestion({
      type: QuestionType.SINGLE_CHOICE,
      options: ['Opcja A', 'Opcja B', 'Opcja C'],
    })

    expect(question.type).toBe(QuestionType.SINGLE_CHOICE)
    expect(question.options).toEqual(['Opcja A', 'Opcja B', 'Opcja C'])
  })

  it('powinien tworzyć pytanie z oceną', () => {
    const question = createMockQuestion({
      type: QuestionType.RATING,
      min_rating: 1,
      max_rating: 10,
    })

    expect(question.type).toBe(QuestionType.RATING)
    expect(question.min_rating).toBe(1)
    expect(question.max_rating).toBe(10)
  })

  it('powinien obsługiwać pytanie niewymagane', () => {
    const question = createMockQuestion({
      required: false,
    })

    expect(question.required).toBe(false)
  })
})

describe('Survey Interface', () => {
  it('powinien tworzyć pełną ankietę', () => {
    const survey = createMockSurvey()

    expect(survey.id).toBeDefined()
    expect(survey.title).toBe('Testowa Ankieta')
    expect(survey.description).toBe('Opis testowej ankiety')
    expect(survey.questions).toHaveLength(2)
    expect(survey.created_at).toBeDefined()
    expect(survey.links).toBeDefined()
  })

  it('powinien mieć poprawne linki', () => {
    const survey = createMockSurvey({ id: 'my-survey' })

    expect(survey.links.survey_url).toContain('my-survey')
    expect(survey.links.stats_url).toContain('my-survey')
  })

  it('powinien obsługiwać brak opisu', () => {
    const survey = createMockSurvey({ description: null })

    expect(survey.description).toBeNull()
  })

  it('powinien obsługiwać wiele pytań', () => {
    const survey = createMockSurvey({ questions: allQuestionTypes })

    expect(survey.questions).toHaveLength(5)
  })
})

describe('SurveyStats Interface', () => {
  it('powinien tworzyć statystyki ankiety', () => {
    const stats = createMockSurveyStats()

    expect(stats.survey_id).toBeDefined()
    expect(stats.survey_title).toBe('Testowa Ankieta')
    expect(stats.total_responses).toBe(25)
    expect(stats.questions_stats).toHaveLength(2)
    expect(stats.created_at).toBeDefined()
    expect(stats.last_response_at).toBeDefined()
  })

  it('powinien obsługiwać brak ostatniej odpowiedzi', () => {
    const stats = createMockSurveyStats({ last_response_at: null })

    expect(stats.last_response_at).toBeNull()
  })

  it('powinien mieć rozkład odpowiedzi', () => {
    const stats = createMockSurveyStats()

    expect(stats.questions_stats[0].answer_distribution).toBeDefined()
    expect(typeof stats.questions_stats[0].total_responses).toBe('number')
  })
})

describe('Answer Interface', () => {
  it('powinien tworzyć odpowiedź tekstową', () => {
    const answer = createMockAnswer({
      question_id: 'q1',
      value: 'Moja odpowiedź',
    })

    expect(answer.question_id).toBe('q1')
    expect(answer.value).toBe('Moja odpowiedź')
  })

  it('powinien obsługiwać różne typy wartości', () => {
    // String
    expect(createMockAnswer({ value: 'tekst' }).value).toBe('tekst')
    
    // Number
    expect(createMockAnswer({ value: 5 }).value).toBe(5)
    
    // Boolean
    expect(createMockAnswer({ value: true }).value).toBe(true)
    
    // Array
    expect(createMockAnswer({ value: ['a', 'b'] }).value).toEqual(['a', 'b'])
  })
})

describe('Factory Functions', () => {
  it('allQuestionTypes powinien zawierać wszystkie typy', () => {
    const types = allQuestionTypes.map(q => q.type)

    expect(types).toContain(QuestionType.TEXT)
    expect(types).toContain(QuestionType.SINGLE_CHOICE)
    expect(types).toContain(QuestionType.MULTIPLE_CHOICE)
    expect(types).toContain(QuestionType.RATING)
    expect(types).toContain(QuestionType.YES_NO)
  })

  it('powinien generować unikalne ID', () => {
    const q1 = createMockQuestion()
    const q2 = createMockQuestion()

    expect(q1.id).not.toBe(q2.id)
  })
})
