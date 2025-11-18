# 4TS Quick Start Guide

**Get started with the Four Tests Standard in 10 minutes**

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
git clone https://github.com/ferz-ai/4ts-standard.git
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

# This validates all example PCDs and generates a conformance report
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
    "models": [{
      "id": "diagnostic-model-v2.1",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }],
    "policies": [{
      "id": "fda-510k-compliance-policy",
      "sha256": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
    }]
  },
  "lineage": [
    {
      "id": "step-1-validation",
      "op": "model_validation",
      "types": {
        "inputs": ["model", "test_dataset"],
        "outputs": ["validation_report"]
      },
      "inputs": ["diagnostic-model-v2.1", "fda-test-set-2025"],
      "outputs": ["validation-report-001"],
      "policy_refs": ["fda-510k-compliance-policy"],
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
    "canonical_hash": "c157a79031e1c40f85931829bc5fc552bf763f332c0e35c0a90e3e3e73e26c41",
    "signatures": [{
      "key_id": "policy-key-001",
      "algorithm": "EdDSA",
      "signature": "5a8c9d2e...",
      "role": "policy"
    }],
    "timestamps": {
      "policy_signed": "2025-10-30T14:00:00Z",
      "exec_start": "2025-10-30T14:30:00Z",
      "exec_end": "2025-10-30T14:35:00Z"
    },
    "key_roles": {
      "policy": ["policy-key-001"],
      "runtime": ["runtime-key-005"]
    }
  }
}
```

### Key Components

| Section | Purpose | Four Tests |
|---------|---------|------------|
| **decision** | What action was taken and when | STOP, ESCALATION |
| **artifacts** | All inputs that influenced the decision | REPLAY |
| **lineage** | Step-by-step execution trace | REPLAY |
| **controls** | Policy enforcement rules | STOP, REPLAY |
| **attestations** | Cryptographic proof of authority | OWNERSHIP |

## Create Your First PCD

### Example: Simple Approval Decision

```python
import json
from datetime import datetime, timezone
import hashlib

def create_simple_pcd(model_id: str, model_sha256: str) -> dict:
    """Create a minimal valid PCD for model deployment"""
    
    now = datetime.now(timezone.utc).isoformat()
    
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
            "canonical_hash": "placeholder",  # Compute after canonicalization
            "signatures": [{
                "key_id": "policy-key-001",
                "algorithm": "EdDSA",
                "signature": "placeholder",  # Sign canonical_hash
                "role": "policy"
            }],
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
    
    return pcd

# Usage
pcd = create_simple_pcd("my-model-v1.0", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
print(json.dumps(pcd, indent=2))
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

- **Questions:** [GitHub Discussions](https://github.com/ferz-ai/4ts-standard/discussions)
- **Issues:** [GitHub Issues](https://github.com/ferz-ai/4ts-standard/issues)
- **Email:** contact@ferzconsulting.com

## Conformance Checklist

To claim 4TS conformance, your implementation must:

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

**© 2025 FERZ LLC** | [4TS Standard](https://github.com/ferz-ai/4ts-standard)
