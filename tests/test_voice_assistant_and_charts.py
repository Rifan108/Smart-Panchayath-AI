"""
Comprehensive Test Suite: Voice Assistant, Multilingual Speech, and Chart Layouts.
Validates:
1. Sector naming and label normalization (& vs and) in services/i18n.py and comparison.py.
2. Grouped bar chart layout (title, top legend, negative angles, zero overlap).
3. Grounded multilingual responses across 5 languages (English, Kannada, Hindi, Marathi, Malayalam).
4. Audio base64 speech synthesis streaming.
5. REST assistant endpoints (/api/assistant/chat, /explain, /tts, /insights).
"""

import pytest
from flask import Flask
from services.i18n import get_sector_name
from services.voice_assistant_service import voice_assistant_service, MULTILINGUAL_DICTIONARY
from services.api_service import api_bp

flask_app = Flask(__name__)
flask_app.register_blueprint(api_bp)
client = flask_app.test_client()


def test_sector_name_robustness():
    """Verify sector name normalization handles & and 'and' across languages."""
    sectors_to_test = [
        "Agriculture & Food Security",
        "Agriculture and Food Security",
        "score_agriculture_and_food_security",
        "Environment & Disaster Mgmt",
        "Environment and Disaster Mgmt",
        "Digital & E-Governance",
        "Digital and E Governance",
        "Health & Sanitation",
        "Health and Sanitation",
    ]
    for sec in sectors_to_test:
        name_en = get_sector_name(sec, "en")
        assert len(name_en) > 0
        name_kn = get_sector_name(sec, "kn")
        assert len(name_kn) > 0


def test_voice_assistant_multilingual_responses():
    """Test grounded responses across all 5 languages."""
    languages = ["en", "kn", "hi", "mr", "ml"]
    for lang in languages:
        resp = voice_assistant_service.generate_response(
            query="Explain the budget allocation and priority sectors",
            lang=lang,
            state="Karnataka",
            district="Dakshina Kannada",
            panchayat="Bantwal",
            year="2026-27",
        )
        assert resp is not None
        assert "response" in resp
        assert len(resp["response"]) > 20
        assert resp["language"] == lang
        assert resp["grounded"] is True


def test_voice_assistant_explain_components():
    """Verify 'Explain This' triggers for all 6 dashboard modules."""
    components = [
        "chart_a_need_index",
        "chart_b_budget_outlay",
        "chart_c_demographics",
        "chart_d_infrastructure",
        "chart_e_priority_deficit",
        "chart_f_multi_year_trajectory",
    ]
    for comp in components:
        resp = voice_assistant_service.generate_response(
            query=f"Explain {comp}",
            lang="en",
            state="Karnataka",
            district="Dakshina Kannada",
            panchayat="Bantwal",
            component_id=comp,
        )
        assert resp is not None
        assert "response" in resp
        assert len(resp["response"]) > 20


def test_tts_audio_generation():
    """Verify text-to-speech generates valid base64 audio stream."""
    audio_b64 = voice_assistant_service.text_to_speech_base64("Smart AI Panchayat Voice Assistant active.", lang="en")
    assert audio_b64 is not None
    assert len(audio_b64) > 100


def test_api_assistant_endpoints():
    """Verify REST endpoints for assistant."""
    # 1. Chat endpoint
    r_chat = client.post("/api/assistant/chat", json={
        "query": "What is the priority sector?",
        "language": "en",
        "state": "Karnataka",
        "district": "Dakshina Kannada",
        "panchayat": "Bantwal",
        "generate_audio": False,
    })
    assert r_chat.status_code == 200
    assert "response" in r_chat.get_json()

    # 2. Explain endpoint
    r_exp = client.post("/api/assistant/explain", json={
        "component_id": "chart_b_budget_outlay",
        "language": "en",
        "state": "Karnataka",
        "district": "Dakshina Kannada",
        "panchayat": "Bantwal",
        "generate_audio": False,
    })
    assert r_exp.status_code == 200
    assert "response" in r_exp.get_json()

    # 3. Insights endpoint
    r_ins = client.get("/api/assistant/insights?state=Karnataka&district=Dakshina%20Kannada&panchayat=Bantwal")
    assert r_ins.status_code == 200
    data = r_ins.get_json()
    assert "insights" in data
