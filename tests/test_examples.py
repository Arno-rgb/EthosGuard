import json
from pathlib import Path

from core.evaluator import evaluate
from core.models import EthicalCheckRequest

EXAMPLES_PATH = Path(__file__).resolve().parents[1] / "examples" / "scenarios.json"
REQUIRED_KEYS = {"id", "title", "scenario", "action", "stakeholders", "expected_verdict"}
VALID_VERDICTS = {"allowed", "risky", "blocked"}


def test_examples_file_loads():
    payload = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    assert len(payload) == 10


def test_examples_have_required_keys():
    payload = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
    for example in payload:
        assert set(example.keys()) == REQUIRED_KEYS


def test_expected_verdicts_are_valid():
    payload = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
    for example in payload:
        assert example["expected_verdict"] in VALID_VERDICTS


def test_showcase_examples_are_deterministic():
    payload = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
    showcase_ids = [
        "hidden-refund-flow",
        "elderly-countdown",
        "safe-recommendation",
    ]
    for example in payload:
        if example["id"] not in showcase_ids:
            continue
        response = evaluate(
            EthicalCheckRequest(
                scenario=example["scenario"],
                action=example["action"],
                stakeholders=example["stakeholders"],
            )
        )
        assert response.provenance.evaluation_mode == "rules"
        assert response.ethical_verdict == example["expected_verdict"]
