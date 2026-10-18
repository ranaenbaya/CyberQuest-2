import pytest

from app import STAGES_BY_ID
from conftest import register_user


def answer_key(stage_id, correct_count):
    quiz = STAGES_BY_ID[stage_id]["quiz"]
    answers = {}
    for index, question in enumerate(quiz):
        answers[str(index)] = (
            question["correct"]
            if index < correct_count
            else next(
                option
                for option in question["options"]
                if option != question["correct"]
            )
        )
    return answers


def test_quiz_score_is_calculated_and_failed_attempt_does_not_save_progress(client):
    register_user(client)

    response = client.post(
        "/api/quiz/submit/hack_1",
        json={"answers": answer_key("hack_1", 3)},
    )

    assert response.status_code == 200
    assert response.json["score"] == 60
    assert response.json["correct"] == 3
    assert response.json["total"] == 5
    assert response.json["passed"] is False
    stages = client.get("/api/stages").json
    assert stages[0]["completed"] is False
    assert stages[1]["unlocked"] is False


def test_passing_quiz_persists_completion_and_unlocks_next_stage(client):
    register_user(client)

    response = client.post(
        "/api/quiz/submit/hack_1",
        json={"answers": answer_key("hack_1", 4)},
    )

    assert response.status_code == 200
    assert response.json["score"] == 80
    assert response.json["passed"] is True
    stages = client.get("/api/stages").json
    hacking_stages = [stage for stage in stages if stage["type"] == "hacking"]
    defence_stages = [stage for stage in stages if stage["type"] == "defence"]
    assert hacking_stages[0]["completed"] is True
    assert hacking_stages[1]["unlocked"] is True
    assert defence_stages[0]["unlocked"] is True
    assert defence_stages[1]["unlocked"] is False


def test_progress_is_private_to_each_user(client):
    register_user(client)
    client.post(
        "/api/quiz/submit/hack_1",
        json={"answers": answer_key("hack_1", 5)},
    )
    client.post("/api/logout")
    register_user(client, username="second-user", email="second@example.com")

    stages = client.get("/api/stages").json
    hacking_stages = [stage for stage in stages if stage["type"] == "hacking"]
    assert hacking_stages[0]["completed"] is False
    assert hacking_stages[1]["unlocked"] is False


@pytest.mark.parametrize("path", ["/api/stages", "/api/quiz/submit/hack_1"])
def test_progress_endpoints_require_login(client, path):
    response = client.get(path) if path == "/api/stages" else client.post(path, json={"answers": {}})

    assert response.status_code == 302
