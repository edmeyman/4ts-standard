#!/usr/bin/env python3
"""
5TS Quickstart Conformance Validator (v1.0.2 bundle)

Performs deterministic structural checks: schema validity, custody,
canonical (envelope) hash equality, timestamp ordering, key role
separation, signature presence, fail-closed and effect-token gating,
lineage typing, and replay consistency.

Out of scope: cryptographic verification of signature values
(E_SIG_INVALID), which requires key material. Full verifiers should
enable it via verifier.config verify_signatures.

Usage:
    python quickstart_validate.py --json path/to/pcd.json
    python quickstart_validate.py --all  # Run the full conformance suite
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

try:
    from jsonschema import ValidationError
    from jsonschema.validators import Draft202012Validator
except ImportError:
    print("Error: jsonschema package required. Install with: pip install jsonschema")
    sys.exit(1)


# Expected results for the v1.0.2 conformance bundle (SPECIFICATION.md section 7.2)
POSITIVE_VECTORS = [
    "PCD-A1_state_auto_approve.json",
    "PCD-A2_protocol_with_gates.json",
    "PCD-A3_fail_closed_denial.json",
]
NEGATIVE_VECTORS = [
    ("NC-1_posthoc_signature.json", "E_PREEXEC_SIGNING"),
    ("NC-2_missing_custody.json", "E_MISSING_CUSTODY"),
    ("NC-3_key_separation.json", "E_KEY_SEPARATION"),
    ("NC-4_untyped_lineage.json", "E_UNTYPED_LINEAGE"),
    ("NC-5_side_effect_on_denial.json", "E_SIDE_EFFECT_ON_DENIAL"),
]


class PCDValidator:
    """Quickstart conformance validator for 5TS PCDs (v1.0.2 bundle)"""

    def __init__(self, schema_path: str = None):
        """Initialize validator with PCD schema"""
        if schema_path is None:
            schema_path = Path(__file__).parent.parent.parent / "schemas" / "pcd.schema.json"

        with open(schema_path) as f:
            self.schema = json.load(f)

        self.validator = Draft202012Validator(self.schema)
        self.errors = []

    def validate_pcd(self, pcd: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate PCD against the v1.0.2 conformance bundle

        Returns: (is_valid, list_of_errors)
        """
        self.errors = []

        # Check 1: Artifact custody (REPLAY test)
        # Runs before schema validation so a missing artifact hash reports
        # the deterministic error code E_MISSING_CUSTODY (section 9.1)
        # rather than a generic schema error.
        if not self._check_artifact_custody(pcd):
            return False, self.errors

        # Check 2: Schema validation
        try:
            self.validator.validate(pcd)
        except ValidationError as e:
            self.errors.append(f"SCHEMA_INVALID: {e.message}")
            return False, self.errors

        # Check 3: Canonical (envelope) hash equality (REPLAY test)
        if not self._check_canonical_hash(pcd):
            return False, self.errors

        # Check 4: Timestamp ordering (OWNERSHIP test)
        if not self._check_timestamp_ordering(pcd):
            return False, self.errors

        # Check 5: Key role separation (OWNERSHIP test)
        if not self._check_key_separation(pcd):
            return False, self.errors

        # Check 6: Signature presence (OWNERSHIP test)
        if not self._check_signatures_present(pcd):
            return False, self.errors

        # Check 7: Fail-closed enforcement and effect-token gating (STOP test)
        if not self._check_fail_closed(pcd):
            return False, self.errors

        # Check 8: Lineage typing (REPLAY test)
        if not self._check_lineage_typing(pcd):
            return False, self.errors

        # Check 9: Replay strategy consistency (REPLAY test)
        if not self._check_replay_consistency(pcd):
            return False, self.errors

        return True, []

    @staticmethod
    def _canonicalize(obj) -> str:
        """Canonical JSON: sorted keys, compact separators, UTF-8."""
        return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'))

    def _check_canonical_hash(self, pcd: Dict[str, Any]) -> bool:
        """
        Verify attestations.canonical_hash equals the SHA-256 of the
        pre-attestation envelope (SPECIFICATION.md section 5): the PCD
        with attestations.canonical_hash removed and every
        attestations.signatures[].signature value blanked.
        """
        declared = pcd.get("attestations", {}).get("canonical_hash")
        if not declared:
            # Absence is reported by schema validation (required field)
            return True

        envelope = json.loads(json.dumps(pcd))  # deep copy
        attestations = envelope.get("attestations", {})
        attestations.pop("canonical_hash", None)
        for sig in attestations.get("signatures", []) or []:
            if isinstance(sig, dict) and "signature" in sig:
                sig["signature"] = ""

        computed = hashlib.sha256(self._canonicalize(envelope).encode('utf-8')).hexdigest()

        if computed != declared:
            self.errors.append(
                "E_HASH_MISMATCH: attestations.canonical_hash does not match "
                "the computed pre-attestation envelope hash"
            )
            return False

        return True

    def _check_signatures_present(self, pcd: Dict[str, Any]) -> bool:
        """
        Verify required signatures are structurally present and consistent:
        at least one policy-role and one runtime-role signature, each with a
        non-empty signature value, and every signature's key_id listed in
        key_roles for its role (approver checked only when key_roles models
        it). Cryptographic verification of the values (E_SIG_INVALID) is out
        of scope for the quickstart validator.
        """
        attestations = pcd.get("attestations", {})
        signatures = attestations.get("signatures", [])
        key_roles = attestations.get("key_roles", {})

        if not signatures:
            self.errors.append("E_SIG_MISSING: attestations.signatures is empty")
            return False

        roles_present = set()
        for sig in signatures:
            if not isinstance(sig, dict):
                continue
            if not sig.get("signature"):
                self.errors.append(
                    f"E_SIG_MISSING: signature value empty for key {sig.get('key_id')}"
                )
                return False

            role = sig.get("role")
            key_id = sig.get("key_id")

            # Structural key-role consistency: a signature only counts for
            # its role if its key_id is listed in key_roles for that role.
            # The approver role is checked only when key_roles models it.
            if role in ("policy", "runtime") or (role == "approver" and "approver" in key_roles):
                authorized_keys = key_roles.get(role, [])
                if key_id not in authorized_keys:
                    self.errors.append(
                        f"E_SIG_MISSING: {role}-role signature uses key "
                        f"{key_id!r} not listed in key_roles.{role}"
                    )
                    return False

            roles_present.add(role)

        for required_role in ("policy", "runtime"):
            if required_role not in roles_present:
                self.errors.append(
                    f"E_SIG_MISSING: no {required_role}-role signature present"
                )
                return False

        return True

    def _check_timestamp_ordering(self, pcd: Dict[str, Any]) -> bool:
        """Verify policy_signed <= exec_start <= exec_end"""
        timestamps = pcd.get("attestations", {}).get("timestamps", {})

        try:
            policy_signed = datetime.fromisoformat(timestamps["policy_signed"].replace('Z', '+00:00'))
            exec_start = datetime.fromisoformat(timestamps["exec_start"].replace('Z', '+00:00'))
            exec_end = datetime.fromisoformat(timestamps["exec_end"].replace('Z', '+00:00'))

            if not (policy_signed <= exec_start <= exec_end):
                self.errors.append("E_PREEXEC_SIGNING: policy_signed must be <= exec_start <= exec_end")
                return False
        except (KeyError, ValueError) as e:
            self.errors.append(f"TIMESTAMP_INVALID: {e}")
            return False

        return True

    def _check_key_separation(self, pcd: Dict[str, Any]) -> bool:
        """Verify policy keys != runtime keys"""
        key_roles = pcd.get("attestations", {}).get("key_roles", {})

        policy_keys = set(key_roles.get("policy", []))
        runtime_keys = set(key_roles.get("runtime", []))

        overlap = policy_keys & runtime_keys
        if overlap:
            self.errors.append(f"E_KEY_SEPARATION: Keys {overlap} used for both policy and runtime")
            return False

        return True

    def _check_fail_closed(self, pcd: Dict[str, Any]) -> bool:
        """Verify fail_closed=true and no effect-token on any non-approved path"""
        controls = pcd.get("controls", {})

        if not controls.get("fail_closed", False):
            self.errors.append("FAIL_CLOSED_REQUIRED: controls.fail_closed must be true")
            return False

        # Effect-tokens MUST NOT exist on denial paths (section 8.3).
        # An escalated outcome blocks execution pending authorized human
        # resolution, so an effect-token on an escalated path is the same
        # violation.
        outcome = pcd.get("decision", {}).get("outcome")
        if outcome in ("denied", "escalated") and pcd.get("effect_token"):
            self.errors.append(
                f"E_SIDE_EFFECT_ON_DENIAL: effect_token present on {outcome} path"
            )
            return False

        return True

    def _check_lineage_typing(self, pcd: Dict[str, Any]) -> bool:
        """Verify all lineage steps have input/output types"""
        lineage = pcd.get("lineage", [])

        for step in lineage:
            types = step.get("types", {})
            if not types.get("inputs") or not types.get("outputs"):
                self.errors.append(f"E_UNTYPED_LINEAGE: Step {step.get('id')} missing types")
                return False

        return True

    def _check_artifact_custody(self, pcd: Dict[str, Any]) -> bool:
        """Verify all artifacts have SHA-256 hashes"""
        artifacts = pcd.get("artifacts", {})
        if not isinstance(artifacts, dict):
            return True  # structural problems are reported by schema validation

        for artifact_type in ["models", "policies", "prompts", "config", "data"]:
            entries = artifacts.get(artifact_type, [])
            if not isinstance(entries, list):
                continue
            for artifact in entries:
                if not isinstance(artifact, dict):
                    continue
                if not artifact.get("sha256"):
                    self.errors.append(f"E_MISSING_CUSTODY: Artifact {artifact.get('id')} missing sha256")
                    return False

                sha256 = artifact.get("sha256", "")
                if not (len(sha256) == 64 and all(c in '0123456789abcdef' for c in sha256)):
                    self.errors.append(f"HASH_INVALID: Artifact {artifact.get('id')} has invalid sha256")
                    return False

        return True

    def _check_replay_consistency(self, pcd: Dict[str, Any]) -> bool:
        """Verify replay strategy matches lineage requirements"""
        replay = pcd.get("controls", {}).get("replay", {})
        strategy = replay.get("strategy")

        if strategy == "protocol":
            # Protocol-replay requires gates
            gates = pcd.get("controls", {}).get("policy_invariants", {}).get("gates", [])
            if not gates:
                self.errors.append("E_PROTOCOL_GATE_MISSING: Protocol-replay requires gates")
                return False

        return True


def validate_file(filepath: str, quiet: bool = False) -> Tuple[bool, List[str]]:
    """Validate a single PCD file. Returns (is_valid, errors)."""
    if not quiet:
        print(f"\n{'='*60}")
        print(f"Validating: {filepath}")
        print('='*60)

    try:
        with open(filepath) as f:
            pcd = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        if not quiet:
            print(f"❌ FAIL: Cannot read file - {e}")
        return False, [f"FILE_ERROR: {e}"]

    validator = PCDValidator()
    is_valid, errors = validator.validate_pcd(pcd)

    if not quiet:
        if is_valid:
            print(f"✅ PASS: PCD is valid")
            print(f"   - Decision ID: {pcd.get('decision', {}).get('id')}")
            print(f"   - Boundary: {pcd.get('decision', {}).get('boundary')}")
            print(f"   - Outcome: {pcd.get('decision', {}).get('outcome')}")
            print(f"   - Replay: {pcd.get('controls', {}).get('replay', {}).get('strategy')}")
        else:
            print(f"❌ FAIL: PCD validation failed")
            for error in errors:
                print(f"   - {error}")

    return is_valid, errors


def run_conformance_suite() -> bool:
    """
    Run the v1.0.2 conformance suite: 3 positive vectors that must PASS
    and 5 negative vectors that must FAIL with the expected error codes
    (SPECIFICATION.md section 7.2).
    """
    repo_root = Path(__file__).parent.parent.parent
    positive_dir = repo_root / "test-vectors" / "positive"
    negative_dir = repo_root / "test-vectors" / "negative"

    print(f"\n{'='*60}")
    print("5TS Conformance Suite — bundle v1.0.2")
    print("3 positive vectors (must PASS), 5 negative vectors")
    print("(must FAIL with expected error codes)")
    print('='*60)

    results = []

    for name in POSITIVE_VECTORS:
        path = positive_dir / name
        is_valid, errors = validate_file(str(path), quiet=True)
        ok = is_valid
        detail = "PASS as expected" if ok else f"expected PASS, got: {errors}"
        results.append((name, ok, detail))

    for name, expected_code in NEGATIVE_VECTORS:
        path = negative_dir / name
        is_valid, errors = validate_file(str(path), quiet=True)
        got_expected = (not is_valid) and any(e.startswith(expected_code) for e in errors)
        if got_expected:
            detail = f"FAIL with {expected_code} as expected"
        elif is_valid:
            detail = f"expected {expected_code}, but vector passed"
        else:
            detail = f"expected {expected_code}, got: {errors}"
        results.append((name, got_expected, detail))

    print()
    ok_count = 0
    for name, ok, detail in results:
        status = "✅" if ok else "❌"
        if ok:
            ok_count += 1
        print(f"{status} {name}: {detail}")

    total = len(results)
    print(f"\n{'='*60}")
    print(f"Conformance result: {ok_count}/{total} vectors behaved as expected")
    print('='*60)

    if ok_count == total:
        print("\nQuickstart validator passes conformance bundle v1.0.2 (8/8 vectors).")
        print("To claim conformance for your own implementation, run these vectors")
        print("through YOUR verifier and publish a conformance claim per")
        print("SPECIFICATION.md section 7.3.")
        return True
    else:
        print(f"\n⚠️  {total - ok_count} vector(s) did not behave as expected. Review above.")
        return False


def run_all_tests() -> bool:
    """Run the conformance suite, then validate the example PCDs."""
    conformance_ok = run_conformance_suite()

    repo_root = Path(__file__).parent.parent.parent
    examples_dir = repo_root / "examples"
    example_files = sorted(examples_dir.glob("*.json"))

    examples_ok = True
    if example_files:
        print(f"\n{'='*60}")
        print(f"Validating {len(example_files)} example PCD(s) (informational)")
        print('='*60)
        for filepath in example_files:
            is_valid, _ = validate_file(str(filepath))
            examples_ok = examples_ok and is_valid

    return conformance_ok and examples_ok


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="5TS PCD Validator (v1.0.2 bundle)")
    parser.add_argument("--json", help="Path to PCD JSON file to validate")
    parser.add_argument("--all", action="store_true",
                        help="Run the conformance suite and validate examples")

    args = parser.parse_args()

    if args.all:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    elif args.json:
        success, _ = validate_file(args.json)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
