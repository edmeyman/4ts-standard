# Four Tests Standard (4TS) - Verifiable AI Governance

**Version:** 1.0.2  
**Steward:** FERZ LLC  
**License:** CC BY-NC-ND 4.0 (specification), MIT (schemas/test vectors)

> **The TCP/IP layer for AI governance**  
> Ensure consequential AI decisions are stop-capable, owned, replayable, and escalatable—by design.

[![SSRN](https://img.shields.io/badge/SSRN-5688982-blue)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5688982)
[![ResearchGate](https://img.shields.io/badge/ResearchGate-Publication-00CCBB)](https://www.researchgate.net/publication/397176413_Verifiable_AI_Governance_The_Four_Tests_Standard_4TS_and_Proof-Carrying_Decisions)

## 📄 Academic Publications

### 📖 Foundational Paper

**Verifiable AI Governance: The Four Tests Standard (4TS) and Proof-Carrying Decisions**  
Edward Meyman | October 2025

Available on:
- [SSRN (Primary)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5688982)
- [ResearchGate](https://www.researchgate.net/publication/397176413_Verifiable_AI_Governance_The_Four_Tests_Standard_4TS_and_Proof-Carrying_Decisions)

*Establishes formal specification, theoretical foundations, and proof of necessary and sufficient conditions for verifiable AI governance.*

---

**How to Cite:**
```
Meyman, E. (2025). Verifiable AI Governance: The Four Tests Standard (4TS) 
and Proof-Carrying Decisions. SSRN. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5688982
```

## Overview

The Four Tests Standard (4TS) is a vendor-neutral technical specification for verifiable AI governance. It enables organizations to prove that AI systems in regulated industries meet compliance requirements through:

- **Proof-Carrying Decisions (PCDs):** Canonical JSON objects encoding all information needed to verify governance at decision boundaries
- **Deterministic Verification:** Mathematical acceptance criteria that produce consistent results independent of who verifies
- **Two Replay Modes:** State-Replay for byte-exact reproduction, Protocol-Replay for gate-based validation
- **Fail-Closed Design:** Actions blocked by default unless approval can be cryptographically proven

## The Four Tests

| Test | Requirement | Enforced Through |
|------|-------------|------------------|
| **STOP** | System can be halted before side-effects | Effect-token issuance gated by approval |
| **OWNERSHIP** | Identified authority signs policy before execution | Cryptographic signatures with timestamp ordering |
| **REPLAY** | Decision can be reproduced at boundary | State-Replay or Protocol-Replay modes |
| **ESCALATION** | Mandatory custody transfer on denial/thresholds | Explicit routing with human-in-loop paths |

## Quick Start

*Enable auditors to verify AI compliance mathematically rather than through sampling—deterministic verification at decision boundaries.*

### Installation

```bash
# Clone the repository
git clone https://github.com/edmeyman/4ts-standard.git
cd 4ts-standard

# Install dependencies (Python 3.10+)
pip install -r requirements.txt
```

### Validate Your First PCD

```bash
# Validate against test vectors
python tools/validator/quickstart_validate.py --json examples/model-deployment-state-replay.json

# Expected output: PASS
```

### Create Your First PCD

```python
from tools import pcd_builder

pcd = pcd_builder.create_pcd(
    boundary="deploy",
    artifacts={"models": [{"id": "my-model-v1.0", "sha256": "..."}]},
    replay_strategy="state"
)

print(pcd.to_json())
```

## Repository Structure

```
4ts-standard/
├── README.md                    # This file
├── SPECIFICATION.md             # Complete technical specification (§§0-11)
├── LICENSE.md                   # Dual license (CC BY-NC-ND 4.0 + MIT)
├── CHANGELOG.md                 # Version history
├── CONTRIBUTING.md              # How to contribute
│
├── schemas/                     # JSON Schema definitions
│   ├── pcd.schema.json         # PCD structure (draft 2020-12)
│   └── verifier.config.schema.json  # Verifier configuration
│
├── examples/                    # Concrete PCD examples
│   ├── model-deployment-state-replay.json
│   ├── rag-system-protocol-replay.json
│   ├── llm-tool-inference.json
│   └── etl-pipeline-batch.json
│
├── test-vectors/                # Conformance test suite
│   ├── positive/               # Must PASS (8 vectors)
│   │   ├── PCD-A1_state_auto_approve.json
│   │   ├── PCD-A2_protocol_with_gates.json
│   │   └── PCD-A3_fail_closed_denial.json
│   └── negative/               # Must FAIL with specific errors (5 vectors)
│       ├── NC-1_posthoc_signature.json
│       ├── NC-2_missing_custody.json
│       ├── NC-3_untyped_lineage.json
│       ├── NC-4_side_effect_on_denial.json
│       └── NC-5_protocol_gate_fail.json
│
├── tools/                       # Reference implementations
│   ├── validator/              # Python reference verifier
│   │   ├── quickstart_validate.py
│   │   └── verifier.py
│   └── canonicalizer/          # JSON canonicalization
│       └── canonicalize.py
│
└── docs/                        # Additional documentation
    ├── quickstart.md           # Getting started guide
    ├── implementation-guide.md # Detailed implementation patterns
    ├── faq.md                  # Frequently asked questions
    └── error-catalog.md        # Complete error code reference
```

## Use Cases

4TS supports diverse AI deployment patterns:

| Profile | PCD Emission | Replay Mode | Key Considerations |
|---------|--------------|-------------|-------------------|
| **LLM Tools** | Per tool action with external effects | State or Protocol | Typed lineage for tool I/O |
| **RAG Systems** | Per response triggering workflows | Protocol (frozen index) | Gates on answerability/attribution |
| **Model Deployment** | At deployment and policy changes | State or Protocol (eval gates) | Pre-exec policy signature required |
| **BPMN/ETL** | Per job with external writes | State or Protocol | Compensating actions for rollbacks |
| **Agentic Systems** | Per plan execution | Protocol with explicit gates | Sub-PCDs for high-risk steps |

## Conformance

To claim 4TS conformance, implementers must:

1. **Pass all test vectors:** 3 positive (PASS), 5 negative (expected failures with correct error codes)
2. **Publish conformance claim:**
   ```
   Tool@Version • PCD-1 • Bundle-1.0.2 • 8/8 • sha256:manifest_hash • logs_link
   ```
3. **Implement core verification:** PCD schema validation, signature verification, replay logic, fail-closed enforcement

See [SPECIFICATION.md](SPECIFICATION.md) §7 for complete conformance requirements.

## Implementation Profiles

### Healthcare/Life Sciences
- **Boundary:** Model deployment for diagnostic/treatment decisions
- **Replay:** State-Replay with frozen training/test sets
- **Gates:** AUROC, calibration error, demographic parity
- **Regulatory:** FDA 510(k), EU MDR alignment

### Financial Services
- **Boundary:** Inference-level for credit/trading decisions
- **Replay:** Protocol-Replay with deterministic risk metrics
- **Gates:** Accuracy, fairness (disparate impact), attribution
- **Regulatory:** SR 11-7, ECOA, MiFID II alignment

### Government/Defense
- **Boundary:** Deploy and policy-change for mission-critical systems
- **Replay:** State-Replay with air-gapped verification
- **Gates:** Security clearance checks, operational safety thresholds
- **Regulatory:** NIST AI RMF, DoD AI principles

## Documentation

- **[Complete Specification](SPECIFICATION.md)** - Full technical standard (§§0-11)
- **[Quick Start Guide](docs/quickstart.md)** - 10-minute implementation tutorial
- **[Implementation Guide](docs/implementation-guide.md)** - Detailed patterns and best practices
- **[FAQ](docs/faq.md)** - Common questions and answers
- **[Error Catalog](docs/error-catalog.md)** - All error codes with triggers and recovery

## Community & Support

- **Issues & Bugs:** [GitHub Issues](https://github.com/edmeyman/4ts-standard/issues)
- **Discussions:** [GitHub Discussions](https://github.com/edmeyman/4ts-standard/discussions)
- **Email:** contact@ferzconsulting.com
- **Website:** https://ferz.ai

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code of conduct
- How to submit issues and pull requests
- Development workflow
- Testing requirements

## Related Standards & Documents

- **[Deterministic AI Governance - Executive Guide](https://ferzconsulting.com/downloads/deterministic-ai-governance-executive-guide.pdf)** - Business rationale and minimum governance bar
- **JSON Schema draft 2020-12** - Schema specification standard
- **RFC 3339 (ISO 8601)** - Timestamp format
- **SHA-256 (FIPS 180-4)** - Cryptographic hashing
- **EdDSA/ECDSA** - Digital signature algorithms

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-09 | Initial release with core standard |
| 1.0.1 | 2025-10 | Added adoption profiles, clarified gate format, expanded error codes |
| 1.0.2 | 2025-11 | Added traceability matrix, glossary, concrete PCD examples |

See [CHANGELOG.md](CHANGELOG.md) for detailed changes.

## License

- **Specification Text:** [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)
  - Attribution required
  - Non-commercial use
  - No derivatives
  
- **Schemas & Test Vectors:** [MIT License](https://opensource.org/licenses/MIT)
  - Permissive use for implementation

See [LICENSE.md](LICENSE.md) for complete terms.

For commercial licensing inquiries: contact@ferzconsulting.com

---

**© 2025 FERZ LLC** | Vendor-neutral open standard for verifiable AI governance
