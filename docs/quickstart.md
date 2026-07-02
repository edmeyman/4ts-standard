# 5TS Quick Start Guide

**Get started with the Five Tests Standard in 10 minutes**

## What You'll Learn

- How to validate a PCD
- How to create your first PCD
- How to run conformance tests
- Basic integration patterns

## Prerequisites

- Python 3.10 or higher
- Basic understanding of JSON
- Command line familiarity

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/edmeyman/4ts-standard.git
cd 4ts-standard
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

## Validate Your First PCD

### Using the Validator

```bash
# Validate a single PCD
python tools/validator/quickstart_validate.py --json examples/model-deployment-state-replay.json

# Expected output:
# ============================================================
# Validating: examples/model-deployment-state-replay.json
# ============================================================
# ✅ PASS: PCD is valid
#    - Decision ID: deploy-diag-model-v2.1
#    - Boundary: deploy
#    - Outcome: approved
#    - Replay: state
```

### Run All Tests

```bash
python tools/validator/quickstart_validate.py --all

# This runs the v1.0.2 conformance suite (3 positive vectors that must
# PASS, 5 negative vectors that must FAIL with the expected error codes)
# and then validates the example PCDs. Expected result: 8/8 vectors
# behaved as expected.
```

## Understanding a PCD

Let's examine the model deployment example:

```json
{
  "pcd_spec_version": "1.0.2",
  "decision": {
    "id": "deploy-diag-model-v2.1",
    "boundary": "deploy",
    "outcome": "approved",
    "effective_window": {
      "start": "2025-11-01T00:00:00Z",
      "end": "2026-11-01T00:00:00Z"
    },
    "routed": false,
    "replayable": true
  },
  "artifacts": {
    "models": [
      {
        "id": "diagnostic-model-v2.1",
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      }
    ],
    "policies": [
      {
        "id": "fda-510k-compliance-policy",
        "sha256": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
      }
    ]
  },
  "lineage": [
    {
      "id": "step-1-validation",
      "op": "model_validation",
      "types": {
        "inputs": [
          "model",
          "test_dataset"
        ],
        "outputs": [
          "validation_report"
        ]
      },
      "inputs": [
        "diagnostic-model-v2.1",
        "fda-test-set-2025"
      ],
      "outputs": [
        "validation-report-001"
      ],
      "policy_refs": [
        "fda-510k-compliance-policy"
      ],
      "stochastic": false
    }
  ],
  "controls": {
    "fail_closed": true,
    "policy_dsl": "internal-v1",
    "replay": {
      "strategy": "state"
    }
  },
  "attestations": {
    "canonical_hash": "0c2e5030dd85cf285468e1dda52d69efa342524df7eb7cba937045032b2ac07a",
    "signatures": [
      {
        "key_id": "policy-key-001",
        "algorithm": "EdDSA",
        "signature": "5a8c9d2e1f3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d",
        "role": "policy"
      },
      {
        "key_id": "runtime-key-005",
        "algorithm": "EdDSA",
        "signature": "bdedf2792a37520df72ede8d05c5954e4c33a2797502bde61e758b0f8c0d2201",
        "role": "runtime"
      }
    ],
    "timestamps": {
      "policy_signed": "2025-10-30T14:00:00Z",
      "exec_start": "2025-10-30T14:30:00Z",
      "exec_end": "2025-10-30T14:35:00Z"
    },
    "key_roles": {
      "policy": [
        "policy-key-001"
      ],
      "runtime": [
        "runtime-key-005"
      ]
    }
  }
}
```

### Key Components

| Section | Purpose | Tests |
|---------|---------|------------|
| **decision** | What action was taken and when | STOP, ESCALATION |
| **artifacts** | All inputs that influenced the decision | REPLAY |
| **lineage** | Step-by-step execution trace | REPLAY |
| **controls** | Policy enforcement rules | STOP, REPLAY |
| **attestations** | Signed, tamper-evident evidence of authority | OWNERSHIP |

## Create Your First PCD

### Example: Simple Approval Decision

```python
import copy
import hashlib
import json
from datetime import datetime, timezone


def compute_canonical_hash(pcd: dict) -> str:
    """
    Compute the PCD canonical_hash over the pre-attestation envelope
    (SPECIFICATION.md section 5): remove attestations.canonical_hash,
    blank every attestations.signatures[].signature value, canonicalize
    (sorted keys, compact separators, UTF-8), then SHA-256.
    """
    envelope = copy.deepcopy(pcd)
    attestations = envelope.get("attestations", {})
    attestations.pop("canonical_hash", None)
    for sig in attestations.get("signatures", []):
        sig["signature"] = ""
    canonical_json = json.dumps(envelope, sort_keys=True, ensure_ascii=False,
                                separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def create_simple_pcd(model_id: str, model_sha256: str) -> dict:
    """Create a minimal valid PCD for model deployment"""

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    pcd = {
        "pcd_spec_version": "1.0.2",
        "decision": {
            "id": f"deploy-{model_id}",
            "boundary": "deploy",
            "outcome": "approved",
            "effective_window": {
                "start": now
            },
            "routed": False,
            "replayable": True
        },
        "artifacts": {
            "models": [{
                "id": model_id,
                "sha256": model_sha256
            }]
        },
        "lineage": [{
            "id": "step-1-validation",
            "op": "model_validation",
            "types": {
                "inputs": ["model"],
                "outputs": ["validation_report"]
            },
            "inputs": [model_id],
            "outputs": ["validation-report-001"],
            "policy_refs": ["default-policy"],
            "stochastic": False
        }],
        "controls": {
            "fail_closed": True,
            "replay": {
                "strategy": "state"
            }
        },
        "attestations": {
            "canonical_hash": "",  # Computed below over the envelope
            "signatures": [
                {
                    "key_id": "policy-key-001",
                    "algorithm": "EdDSA",
                    # Demo value. Real systems sign the canonical_hash with
                    # the policy key; signature values are excluded from the
                    # hash envelope, so signing happens after hashing.
                    "signature": "demo-policy-signature",
                    "role": "policy"
                },
                {
                    "key_id": "runtime-key-001",
                    "algorithm": "EdDSA",
                    "signature": "demo-runtime-signature",
                    "role": "runtime"
                }
            ],
            "timestamps": {
                "policy_signed": now,
                "exec_start": now,
                "exec_end": now
            },
            "key_roles": {
                "policy": ["policy-key-001"],
                "runtime": ["runtime-key-001"]
            }
        }
    }

    # Envelope flow: hash first (signature values excluded), then sign.
    pcd["attestations"]["canonical_hash"] = compute_canonical_hash(pcd)

    return pcd


# Usage
pcd = create_simple_pcd("my-model-v1.0",
                        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
print(json.dumps(pcd, indent=2))
```

The demo signature values pass the validator's structural checks; production
systems replace them with real signatures over the canonical_hash. Save the
output and validate it:

```bash
python tools/validator/quickstart_validate.py --json my-first-pcd.json
```

## Common Patterns

### Pattern 1: State-Replay (Deterministic)

**When to use:** All artifacts are frozen and byte-stable

```json
{
  "controls": {
    "fail_closed": true,
    "replay": {
      "strategy": "state"
    }
  }
}
```

**Requirements:**
- All artifacts must have SHA-256 hashes
- Lineage steps must be deterministic (`"stochastic": false`)
- PCD canonical_hash must match on replay

### Pattern 2: Protocol-Replay (Stochastic OK)

**When to use:** Some steps are non-deterministic but validation gates are deterministic

```json
{
  "controls": {
    "fail_closed": true,
    "replay": {
      "strategy": "protocol"
    },
    "policy_invariants": {
      "gates": [{
        "id": "gate-1-accuracy",
        "metric": "accuracy",
        "dataset": "eval-set-v1",
        "op": ">=",
        "value": 0.95
      }]
    }
  }
}
```

**Requirements:**
- Gates must be deterministic even if steps aren't
- Frozen datasets for gate evaluation
- Gate outcomes must match on replay

## Next Steps

### Learn More

- **[Complete Specification](../SPECIFICATION.md)** - Full technical details
- **[Implementation Guide](implementation-guide.md)** - Advanced patterns
- **[FAQ](faq.md)** - Common questions
- **[Error Catalog](error-catalog.md)** - All error codes

### Try It Out

1. **Modify an example PCD**
   - Change the decision outcome
   - Add a new artifact
   - Add a lineage step

2. **Run the validator**
   ```bash
   python tools/validator/quickstart_validate.py --json your-pcd.json
   ```

3. **Understand any errors**
   - Check [Error Catalog](error-catalog.md) for details
   - Review [Specification](../SPECIFICATION.md) requirements

### Get Help

- **Questions:** [GitHub Discussions](https://github.com/edmeyman/4ts-standard/discussions)
- **Issues:** [GitHub Issues](https://github.com/edmeyman/4ts-standard/issues)
- **Email:** info@ferz.ai

## Conformance Checklist

To claim conformance to the v1.0.2 conformance bundle (four of the five tests; Provenance conformance is not yet assertable), your implementation must:

- [ ] Pass PCD schema validation
- [ ] Enforce timestamp ordering (policy_signed ≤ exec_start ≤ exec_end)
- [ ] Enforce key role separation (policy keys ≠ runtime keys)
- [ ] Require fail_closed = true
- [ ] Include types for all lineage steps
- [ ] Include SHA-256 hashes for all artifacts
- [ ] Match replay strategy to lineage (state vs protocol)
- [ ] Pass all 8 conformance test vectors (3 positive, 5 negative)

See [SPECIFICATION.md](../SPECIFICATION.md) §7 for complete requirements.

---

**© 2025–2026 FERZ, Inc.** | [5TS Standard](https://github.com/edmeyman/4ts-standard)
