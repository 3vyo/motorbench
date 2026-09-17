from httpx2 import head
import pytest
from fastapi.testclient import TestClient

from Database import Base
from Main import app, get_db
from testing.test_db import TestingSessionLocal, test_engine


def override_get_db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)

def question_payload(question_text="What is the capital of France?"):
    return {
        "question_text": question_text,
        "choices": [
            {"choice_text": "Paris", "is_correct": True},
            {"choice_text": "London", "is_correct": False},
            {"choice_text": "Berlin", "is_correct": False},
            {"choice_text": "Madrid", "is_correct": False},
        ],
    }


def create_question(client, question_text="What is the capital of France?"):
    response = client.post(
        "/questions/",
        json=question_payload(question_text),
    )
    assert response.status_code == 201
    return response.json()


def test_read_main(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Quiz API is running",
        "docs": "/docs",
    }


def test_create_question(client):
    question = create_question(client)

    assert isinstance(question["id"], int)
    assert question["question_text"] == "What is the capital of France?"
    assert [choice["choice_text"] for choice in question["choices"]] == [
        "Paris",
        "London",
        "Berlin",
        "Madrid",
    ]
    assert [choice["is_correct"] for choice in question["choices"]] == [
        True,
        False,
        False,
        False,
    ]


def test_read_question(client):
    created_question = create_question(client)

    response = client.get(
        "/questions/",
        params={"question_id": created_question["id"]},
    )

    assert response.status_code == 200
    assert response.json()["id"] == created_question["id"]
    assert response.json()["question_text"] == created_question["question_text"]


def test_read_choices(client):
    created_question = create_question(client)

    response = client.get(f"/choices/{created_question['id']}")

    assert response.status_code == 200
    choices = response.json()
    assert [choice["choice_text"] for choice in choices] == [
        "Paris",
        "London",
        "Berlin",
        "Madrid",
    ]
    assert sum(choice["is_correct"] for choice in choices) == 1


def test_read_question_not_found(client):
    response = client.get("/questions/", params={"question_id": 999})

    assert response.status_code == 404
    assert response.json() == {"detail": "Question not Found"}


def test_read_choices_not_found(client):
    response = client.get("/choices/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "choice not Found"}


def test_create_question_rejects_blank_text(client):
    response = client.post(
        "/questions/",
        json=question_payload("   "),
    )

    assert response.status_code == 422
    error_locations = [error["loc"] for error in response.json()["detail"]]
    assert ["body", "question_text"] in error_locations


def test_create_question_requires_at_least_two_choices(client):
    payload = question_payload()
    payload["choices"] = payload["choices"][:1]

    response = client.post("/questions/", json=payload)

    assert response.status_code == 422
    error_locations = [error["loc"] for error in response.json()["detail"]]
    assert ["body", "choices"] in error_locations


def test_create_question_requires_exactly_one_correct_choice(client):
    payload = question_payload()
    payload["choices"][1]["is_correct"] = True

    response = client.post("/questions/", json=payload)

    assert response.status_code == 422
    assert "exactly one correct choice" in response.text
