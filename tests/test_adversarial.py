from core.evaluators import run_suite
from tests.adversarial_cases import ADVERSARIAL_CASES


def test_adversarial_suite():
    results = run_suite(ADVERSARIAL_CASES)
    failures = [result for result in results if not result.passed]
    assert not failures, failures


def test_suite_covers_bypass_and_self_preservation_families():
    families = {case.family for case in ADVERSARIAL_CASES}
    assert "shutdown_acceptance" in families
    assert "self_exfiltration" in families
    assert "specification_gaming" in families
    assert "audit_log_manipulation" in families
