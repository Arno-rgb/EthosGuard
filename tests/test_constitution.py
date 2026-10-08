import json
from pathlib import Path

from core.constitution import constitution_hash, hard_constraint_ids, load_constitution

ROOT = Path(__file__).resolve().parents[1]


def test_constitution_is_valid_and_hard_constraints_are_immutable():
    data = load_constitution()
    assert data["constitution_version"] == "2.0.0-draft"
    assert len(hard_constraint_ids()) == 15
    assert all(item["mutable"] is False for item in data["hard_constraints"])


def test_constitution_json_is_hashable_and_source_hash_is_pinned():
    data = json.loads((ROOT / "constitution.json").read_text(encoding="utf-8"))
    assert len(constitution_hash()) == 64
    assert data["source_sha256"] == "eac5ae22f883777d78bec0d147602dd96711df5c727267f9bcdf0057db4df672"
