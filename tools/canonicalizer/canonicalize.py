#!/usr/bin/env python3
"""
5TS JSON Canonicalizer
Produces the canonical JSON representation used for PCD hashing.

The canonical form sorts keys recursively, uses compact separators,
and preserves UTF-8 (see docs/implementation-guide.md, PCD Generation
Pipeline).

Usage:
    python canonicalize.py path/to/pcd.json          # print canonical JSON
    python canonicalize.py --hash path/to/pcd.json   # print SHA-256 of canonical form
"""

import argparse
import hashlib
import json
import sys


def canonicalize(obj) -> str:
    """Produce canonical JSON representation."""
    # Sort keys recursively, normalize separators, UTF-8 encoding
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def canonical_hash(obj) -> str:
    """Compute deterministic SHA-256 hash of the canonical JSON form."""
    return hashlib.sha256(canonicalize(obj).encode('utf-8')).hexdigest()


def pcd_envelope(pcd: dict) -> dict:
    """
    Build the pre-attestation hash envelope defined in SPECIFICATION.md
    section 5: remove attestations.canonical_hash and blank every
    attestations.signatures[].signature value.
    """
    envelope = json.loads(json.dumps(pcd))  # deep copy
    attestations = envelope.get("attestations", {})
    if isinstance(attestations, dict):
        attestations.pop("canonical_hash", None)
        signatures = attestations.get("signatures", [])
        if isinstance(signatures, list):
            for sig in signatures:
                if isinstance(sig, dict) and "signature" in sig:
                    sig["signature"] = ""
    return envelope


def pcd_canonical_hash(pcd: dict) -> str:
    """Compute the PCD canonical_hash over the pre-attestation envelope."""
    return canonical_hash(pcd_envelope(pcd))


def main():
    parser = argparse.ArgumentParser(description="5TS JSON canonicalizer")
    parser.add_argument("path", help="Path to a JSON file")
    parser.add_argument("--hash", action="store_true",
                        help="Print the SHA-256 hash of the canonical form")
    parser.add_argument("--pcd-hash", action="store_true",
                        help="Print the PCD canonical_hash (pre-attestation envelope)")
    args = parser.parse_args()

    try:
        with open(args.path) as f:
            obj = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error: cannot read {args.path}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.pcd_hash:
        print(pcd_canonical_hash(obj))
    elif args.hash:
        print(canonical_hash(obj))
    else:
        print(canonicalize(obj))


if __name__ == "__main__":
    main()
