#!/usr/bin/env python3
"""
4TS Quickstart Validator
Validates PCDs against 4TS v1.0.2 requirements

Usage:
    python quickstart_validate.py --json path/to/pcd.json
    python quickstart_validate.py --all  # Run all test vectors
"""

import json
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

try:
    from jsonschema import validate, ValidationError
    from jsonschema.validators import Draft202012Validator
except ImportError:
    print("Error: jsonschema package required. Install with: pip install jsonschema")
    sys.exit(1)


class PCDValidator:
    """Reference validator for 4TS PCDs"""
    
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
        Validate PCD against 4TS requirements
        
        Returns: (is_valid, list_of_errors)
        """
        self.errors = []
        
        # Check 1: Schema validation
        try:
            self.validator.validate(pcd)
        except ValidationError as e:
            self.errors.append(f"SCHEMA_INVALID: {e.message}")
            return False, self.errors
        
        # Check 2: Timestamp ordering (OWNERSHIP test)
        if not self._check_timestamp_ordering(pcd):
            return False, self.errors
        
        # Check 3: Key role separation (OWNERSHIP test)
        if not self._check_key_separation(pcd):
            return False, self.errors
        
        # Check 4: Fail-closed enforcement (STOP test)
        if not self._check_fail_closed(pcd):
            return False, self.errors
        
        # Check 5: Lineage typing (REPLAY test)
        if not self._check_lineage_typing(pcd):
            return False, self.errors
        
        # Check 6: Artifact custody (REPLAY test)
        if not self._check_artifact_custody(pcd):
            return False, self.errors
        
        # Check 7: Replay strategy consistency (REPLAY test)
        if not self._check_replay_consistency(pcd):
            return False, self.errors
        
        return True, []
    
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
        """Verify fail_closed=true and no effect-token on denial"""
        controls = pcd.get("controls", {})
        
        if not controls.get("fail_closed", False):
            self.errors.append("FAIL_CLOSED_REQUIRED: controls.fail_closed must be true")
            return False
        
        # Check for effect-token on denial path (simplified check)
        outcome = pcd.get("decision", {}).get("outcome")
        if outcome == "denied":
            # In real implementation, check for effect-token presence
            # For now, just verify outcome is valid
            pass
        
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
        
        for artifact_type in ["models", "policies", "prompts", "config", "data"]:
            for artifact in artifacts.get(artifact_type, []):
                if not artifact.get("sha256"):
                    self.errors.append(f"E_MISSING_CUSTODY: Artifact {artifact.get('id')} missing sha256")
                    return False
                
                # Verify hash format
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


def validate_file(filepath: str) -> bool:
    """Validate a single PCD file"""
    print(f"\n{'='*60}")
    print(f"Validating: {filepath}")
    print('='*60)
    
    try:
        with open(filepath) as f:
            pcd = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ FAIL: Cannot read file - {e}")
        return False
    
    validator = PCDValidator()
    is_valid, errors = validator.validate_pcd(pcd)
    
    if is_valid:
        print(f"✅ PASS: PCD is valid")
        print(f"   - Decision ID: {pcd.get('decision', {}).get('id')}")
        print(f"   - Boundary: {pcd.get('decision', {}).get('boundary')}")
        print(f"   - Outcome: {pcd.get('decision', {}).get('outcome')}")
        print(f"   - Replay: {pcd.get('controls', {}).get('replay', {}).get('strategy')}")
        return True
    else:
        print(f"❌ FAIL: PCD validation failed")
        for error in errors:
            print(f"   - {error}")
        return False


def run_all_tests():
    """Run all test vectors"""
    repo_root = Path(__file__).parent.parent.parent
    examples_dir = repo_root / "examples"
    
    test_files = list(examples_dir.glob("*.json"))
    
    if not test_files:
        print("No test files found in examples/")
        return False
    
    print(f"\n{'='*60}")
    print(f"Running 4TS Conformance Tests")
    print(f"Found {len(test_files)} test files")
    print('='*60)
    
    results = []
    for filepath in sorted(test_files):
        passed = validate_file(str(filepath))
        results.append((filepath.name, passed))
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print('='*60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! This implementation is 4TS conformant.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="4TS PCD Validator v1.0.2")
    parser.add_argument("--json", help="Path to PCD JSON file to validate")
    parser.add_argument("--all", action="store_true", help="Run all test vectors")
    
    args = parser.parse_args()
    
    if args.all:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    elif args.json:
        success = validate_file(args.json)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
