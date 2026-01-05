"""
Testy End-to-End - pełne żądania HTTP przez API.
"""
import pytest
from uuid import uuid4


class TestHealthEndpoints:
    """Testy endpointów health."""
    
    def test_root_endpoint(self, client):
        """Sprawdza główny endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Polly Survey API"
        assert "version" in data
    
    def test_health_endpoint(self, client):
        """Sprawdza endpoint health."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "singletons" in data
        assert "database" in data["singletons"]
        assert "logger" in data["singletons"]
        assert "config" in data["singletons"]


class TestSurveyCreationE2E:
    """Testy E2E tworzenia ankiet."""
    
    def test_create_survey_success(self, client):
        """Sprawdza pomyślne tworzenie ankiety."""
        survey_data = {
            "title": "E2E Test Survey",
            "description": "Test description",
            "questions": [
                {
                    "id": "q1",
                    "text": "What is your name?",
                    "type": "text",
                    "required": True,
                }
            ],
        }
        
        response = client.post("/surveys/", json=survey_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "E2E Test Survey"
        assert "id" in data
        assert "links" in data
        assert "survey_url" in data["links"]
        assert "stats_url" in data["links"]
    
    def test_create_survey_with_all_question_types(self, client):
        """Sprawdza tworzenie ankiety ze wszystkimi typami pytań."""
        survey_data = {
            "title": "Full Survey",
            "questions": [
                {"id": "q1", "text": "Name?", "type": "text"},
                {"id": "q2", "text": "Color?", "type": "single_choice", 
                 "options": ["Red", "Blue"]},
                {"id": "q3", "text": "Languages?", "type": "multiple_choice",
                 "options": ["Python", "JS"], "required": False},
                {"id": "q4", "text": "Rate?", "type": "rating",
                 "min_rating": 1, "max_rating": 5},
                {"id": "q5", "text": "Recommend?", "type": "yes_no"},
            ],
        }
        
        response = client.post("/surveys/", json=survey_data)
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["questions"]) == 5
    
    def test_create_survey_invalid_title(self, client):
        """Sprawdza błąd przy pustym tytule."""
        survey_data = {
            "title": "",
            "questions": [
                {"id": "q1", "text": "Test?", "type": "text"}
            ],
        }
        
        response = client.post("/surveys/", json=survey_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_survey_no_questions(self, client):
        """Sprawdza błąd przy braku pytań."""
        survey_data = {
            "title": "Empty Survey",
            "questions": [],
        }
        
        response = client.post("/surveys/", json=survey_data)
        
        assert response.status_code == 422


class TestSurveyRetrievalE2E:
    """Testy E2E pobierania ankiet."""
    
    def test_get_survey_success(self, client):
        """Sprawdza pobieranie istniejącej ankiety."""
        # Najpierw tworzenie
        survey_data = {
            "title": "Test Survey",
            "questions": [
                {"id": "q1", "text": "Test?", "type": "text"}
            ],
        }
        create_response = client.post("/surveys/", json=survey_data)
        survey_id = create_response.json()["id"]
        
        # Pobieranie
        response = client.get(f"/surveys/{survey_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == survey_id
        assert data["title"] == "Test Survey"
    
    def test_get_survey_not_found(self, client):
        """Sprawdza błąd dla nieistniejącej ankiety."""
        fake_id = str(uuid4())
        
        response = client.get(f"/surveys/{fake_id}")
        
        assert response.status_code == 404
    
    def test_get_survey_invalid_uuid(self, client):
        """Sprawdza błąd dla niepoprawnego UUID."""
        response = client.get("/surveys/not-a-uuid")
        
        assert response.status_code == 422
    
    def test_get_all_surveys(self, client):
        """Sprawdza pobieranie wszystkich ankiet."""
        # Tworzenie kilku ankiet
        for i in range(3):
            survey_data = {
                "title": f"Survey {i}",
                "questions": [
                    {"id": "q1", "text": "Test?", "type": "text"}
                ],
            }
            client.post("/surveys/", json=survey_data)
        
        # Pobieranie wszystkich
        response = client.get("/surveys/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3


class TestSubmitResponseE2E:
    """Testy E2E wysyłania odpowiedzi."""
    
    def test_submit_response_success(self, client):
        """Sprawdza pomyślne wysłanie odpowiedzi."""
        # Tworzenie ankiety
        survey_data = {
            "title": "Response Test",
            "questions": [
                {"id": "q1", "text": "Name?", "type": "text", "required": True},
            ],
        }
        survey_response = client.post("/surveys/", json=survey_data)
        survey_id = survey_response.json()["id"]
        
        # Wysyłanie odpowiedzi
        answer_data = {
            "answers": [
                {"question_id": "q1", "value": "John Doe"}
            ],
            "respondent_id": "user-123",
        }
        
        response = client.post(f"/surveys/{survey_id}/responses", json=answer_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["survey_id"] == survey_id
        assert data["respondent_id"] == "user-123"
    
    def test_submit_response_missing_required(self, client):
        """Sprawdza błąd przy brakującej wymaganej odpowiedzi."""
        # Tworzenie ankiety
        survey_data = {
            "title": "Required Test",
            "questions": [
                {"id": "q1", "text": "Required?", "type": "text", "required": True},
                {"id": "q2", "text": "Optional?", "type": "text", "required": False},
            ],
        }
        survey_response = client.post("/surveys/", json=survey_data)
        survey_id = survey_response.json()["id"]
        
        # Brak odpowiedzi na wymagane pytanie
        answer_data = {
            "answers": [
                {"question_id": "q2", "value": "Optional answer"}
            ],
        }
        
        response = client.post(f"/surveys/{survey_id}/responses", json=answer_data)
        
        assert response.status_code == 400
    
    def test_submit_response_invalid_choice(self, client):
        """Sprawdza błąd przy nieprawidłowej opcji wyboru."""
        # Tworzenie ankiety
        survey_data = {
            "title": "Choice Test",
            "questions": [
                {
                    "id": "q1", 
                    "text": "Color?", 
                    "type": "single_choice",
                    "options": ["Red", "Blue", "Green"],
                },
            ],
        }
        survey_response = client.post("/surveys/", json=survey_data)
        survey_id = survey_response.json()["id"]
        
        # Nieprawidłowa opcja
        answer_data = {
            "answers": [
                {"question_id": "q1", "value": "Yellow"}  # Nie ma takiej opcji
            ],
        }
        
        response = client.post(f"/surveys/{survey_id}/responses", json=answer_data)
        
        assert response.status_code == 400
    
    def test_submit_response_invalid_rating(self, client):
        """Sprawdza błąd przy ocenie poza zakresem."""
        # Tworzenie ankiety
        survey_data = {
            "title": "Rating Test",
            "questions": [
                {
                    "id": "q1",
                    "text": "Rate?",
                    "type": "rating",
                    "min_rating": 1,
                    "max_rating": 5,
                },
            ],
        }
        survey_response = client.post("/surveys/", json=survey_data)
        survey_id = survey_response.json()["id"]
        
        # Ocena poza zakresem
        answer_data = {
            "answers": [
                {"question_id": "q1", "value": 10}  # Max to 5
            ],
        }
        
        response = client.post(f"/surveys/{survey_id}/responses", json=answer_data)
        
        assert response.status_code == 400
    
    def test_submit_response_survey_not_found(self, client):
        """Sprawdza błąd dla nieistniejącej ankiety."""
        fake_id = str(uuid4())
        answer_data = {
            "answers": [
                {"question_id": "q1", "value": "test"}
            ],
        }
        
        response = client.post(f"/surveys/{fake_id}/responses", json=answer_data)
        
        assert response.status_code == 400  # ValueError -> 400
    
    def test_submit_anonymous_response(self, client):
        """Sprawdza anonimowe wysyłanie odpowiedzi."""
        # Tworzenie ankiety
        survey_data = {
            "title": "Anonymous Test",
            "questions": [
                {"id": "q1", "text": "Test?", "type": "text"},
            ],
        }
        survey_response = client.post("/surveys/", json=survey_data)
        survey_id = survey_response.json()["id"]
        
        # Odpowiedź bez respondent_id
        answer_data = {
            "answers": [
                {"question_id": "q1", "value": "Anonymous answer"}
            ],
        }
        
        response = client.post(f"/surveys/{survey_id}/responses", json=answer_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["respondent_id"] is None


class TestStatisticsE2E:
    """Testy E2E statystyk ankiet."""
    
    def test_get_statistics_empty(self, client):
        """Sprawdza statystyki bez odpowiedzi."""
        # Tworzenie ankiety
        survey_data = {
            "title": "Stats Test",
            "questions": [
                {"id": "q1", "text": "Test?", "type": "text"},
            ],
        }
        survey_response = client.post("/surveys/", json=survey_data)
        survey_id = survey_response.json()["id"]
        
        # Pobieranie statystyk
        response = client.get(f"/surveys/{survey_id}/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["survey_id"] == survey_id
        assert data["total_responses"] == 0
    
    def test_get_statistics_with_responses(self, client):
        """Sprawdza statystyki z odpowiedziami."""
        # Tworzenie ankiety
        survey_data = {
            "title": "Stats Test",
            "questions": [
                {"id": "q1", "text": "Name?", "type": "text"},
                {"id": "q2", "text": "Rate?", "type": "rating", 
                 "min_rating": 1, "max_rating": 5},
            ],
        }
        survey_response = client.post("/surveys/", json=survey_data)
        survey_id = survey_response.json()["id"]
        
        # Wysyłanie odpowiedzi
        for i in range(5):
            answer_data = {
                "answers": [
                    {"question_id": "q1", "value": f"User {i}"},
                    {"question_id": "q2", "value": i + 1},
                ],
            }
            client.post(f"/surveys/{survey_id}/responses", json=answer_data)
        
        # Pobieranie statystyk
        response = client.get(f"/surveys/{survey_id}/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_responses"] == 5
        assert data["last_response_at"] is not None
        
        # Sprawdzenie średniej
        rating_stats = next(
            q for q in data["questions_stats"] if q["question_id"] == "q2"
        )
        assert rating_stats["average_value"] == 3.0  # (1+2+3+4+5)/5
    
    def test_get_statistics_not_found(self, client):
        """Sprawdza błąd dla nieistniejącej ankiety."""
        fake_id = str(uuid4())
        
        response = client.get(f"/surveys/{fake_id}/stats")
        
        assert response.status_code == 404


class TestCompleteWorkflowE2E:
    """Testy pełnego przepływu E2E."""
    
    def test_full_survey_lifecycle(self, client):
        """Sprawdza pełny cykl życia ankiety."""
        # 1. Tworzenie ankiety
        survey_data = {
            "title": "Customer Satisfaction Survey",
            "description": "Please rate our service",
            "questions": [
                {"id": "name", "text": "Your name", "type": "text", "required": False},
                {"id": "rating", "text": "Rate our service", "type": "rating",
                 "min_rating": 1, "max_rating": 10},
                {"id": "recommend", "text": "Would you recommend us?", "type": "yes_no"},
                {"id": "features", "text": "Which features do you like?", 
                 "type": "multiple_choice",
                 "options": ["Speed", "Quality", "Price", "Support"],
                 "required": False},
            ],
        }
        
        create_response = client.post("/surveys/", json=survey_data)
        assert create_response.status_code == 201
        survey = create_response.json()
        survey_id = survey["id"]
        
        # 2. Pobieranie ankiety
        get_response = client.get(f"/surveys/{survey_id}")
        assert get_response.status_code == 200
        
        # 3. Wysyłanie odpowiedzi od różnych użytkowników
        responses_data = [
            {
                "answers": [
                    {"question_id": "name", "value": "Alice"},
                    {"question_id": "rating", "value": 9},
                    {"question_id": "recommend", "value": "yes"},
                    {"question_id": "features", "value": ["Speed", "Quality"]},
                ],
                "respondent_id": "alice@example.com",
            },
            {
                "answers": [
                    {"question_id": "name", "value": "Bob"},
                    {"question_id": "rating", "value": 7},
                    {"question_id": "recommend", "value": "yes"},
                    {"question_id": "features", "value": ["Price"]},
                ],
                "respondent_id": "bob@example.com",
            },
            {
                "answers": [
                    {"question_id": "rating", "value": 5},
                    {"question_id": "recommend", "value": "no"},
                ],  # Anonimowa odpowiedź z minimalnymi danymi
            },
        ]
        
        for resp_data in responses_data:
            resp = client.post(f"/surveys/{survey_id}/responses", json=resp_data)
            assert resp.status_code == 201
        
        # 4. Pobieranie statystyk
        stats_response = client.get(f"/surveys/{survey_id}/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        assert stats["total_responses"] == 3
        assert stats["survey_title"] == "Customer Satisfaction Survey"
        
        # Sprawdzenie średniej oceny
        rating_stats = next(
            q for q in stats["questions_stats"] if q["question_id"] == "rating"
        )
        assert rating_stats["total_responses"] == 3
        expected_avg = (9 + 7 + 5) / 3
        assert abs(rating_stats["average_value"] - expected_avg) < 0.01
        
        # Sprawdzenie rozkładu recommend
        recommend_stats = next(
            q for q in stats["questions_stats"] if q["question_id"] == "recommend"
        )
        assert recommend_stats["answer_distribution"]["yes"] == 2
        assert recommend_stats["answer_distribution"]["no"] == 1
        
        # 5. Sprawdzenie listy wszystkich ankiet
        all_surveys = client.get("/surveys/")
        assert all_surveys.status_code == 200
        assert any(s["id"] == survey_id for s in all_surveys.json())
    
    def test_multiple_surveys_workflow(self, client):
        """Sprawdza przepływ z wieloma ankietami."""
        surveys = []
        
        # Tworzenie 3 ankiet
        for i in range(3):
            survey_data = {
                "title": f"Survey {i + 1}",
                "questions": [
                    {"id": "q1", "text": "Question?", "type": "text"},
                ],
            }
            response = client.post("/surveys/", json=survey_data)
            surveys.append(response.json())
        
        # Wysyłanie odpowiedzi do każdej ankiety
        for survey in surveys:
            for j in range(2):
                answer_data = {
                    "answers": [
                        {"question_id": "q1", "value": f"Answer {j}"}
                    ],
                }
                client.post(f"/surveys/{survey['id']}/responses", json=answer_data)
        
        # Weryfikacja statystyk każdej ankiety
        for survey in surveys:
            stats_response = client.get(f"/surveys/{survey['id']}/stats")
            stats = stats_response.json()
            assert stats["total_responses"] == 2
        
        # Weryfikacja listy
        all_surveys = client.get("/surveys/").json()
        assert len(all_surveys) >= 3
