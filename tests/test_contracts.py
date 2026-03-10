from core.models import EthicalCheckResponse, ExtractedSignals, Provenance


def test_response_schema_is_frozen():
    properties = EthicalCheckResponse.model_json_schema()["properties"]
    assert list(properties.keys()) == [
        "ethical_verdict",
        "risk_score",
        "principles_triggered",
        "explanation",
        "recommended_action",
        "provenance",
        "extracted_signals",
    ]


def test_provenance_schema_is_frozen():
    properties = Provenance.model_json_schema()["properties"]
    assert list(properties.keys()) == [
        "evaluation_mode",
        "rules_matched",
        "llm_used",
        "llm_model",
        "policy_version",
        "confidence",
    ]


def test_extracted_signals_schema_is_frozen():
    properties = ExtractedSignals.model_json_schema()["properties"]
    assert list(properties.keys()) == [
        "harm",
        "deception",
        "vulnerable_target",
        "privacy_misuse",
        "unsafe_concealment",
        "power_asymmetry",
        "financial_pressure",
        "child_targeting",
    ]
