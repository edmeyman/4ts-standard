# Five Tests Standard (5TS) - Verifiable AI Governance

**Version:** 1.2.0  
**Steward:** FERZ, Inc.  
**License:** CC BY-NC-ND 4.0 (specification/docs), MIT (schemas/examples/tools/test vectors)

> **A conformance layer for verifiable AI governance**  
> Ensure consequential AI decisions are stop-capable, owned, replayable, escalation-capable, and grounded in inputs of established origin.

[![SSRN](https://img.shields.io/badge/SSRN-5688982-blue)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5688982)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21040295.svg)](https://doi.org/10.5281/zenodo.21040295)

## 📄 Academic Publications

### 📖 Foundational Paper

**Verifiable AI Governance: The Five Tests Standard (5TS) and Proof-Carrying Decisions**  
Edward Meyman | October 2025; revised June 2026

Available on:
- [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5688982)

*Establishes the formal specification, theoretical foundations, and conformance framing for verifiable AI governance through proof-carrying decisions.*

---

**How to Cite:**
```
Meyman, E. (2025). Verifiable AI Governance: The Five Tests Standard (5TS) 
and Proof-Carrying Decisions. SSRN. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5688982
```

**Cite the standard:**
```
Meyman, E. (2026). The Five Tests Standard (5TS), v1.2.0. Zenodo.
Concept DOI (all versions): https://doi.org/10.5281/zenodo.21040295
This version (v1.2.0): https://doi.org/10.5281/zenodo.21040296
```

## Overview

The Five Tests Standard (5TS) is a vendor-neutral technical specification for verifiable AI governance. It enables organizations to produce verifiable evidence that AI decisions in regulated industries are governed under a specific policy and authority, through:

- **Proof-Carrying Decisions (PCDs):** Canonical JSON objects encoding all information needed to verify governance at decision boundaries
- **Deterministic Verification:** Mathematical acceptance criteria that produce consistent results independent of who verifies
- **Two Replay Modes:** State-Replay for byte-exact reproduction, Protocol-Replay for gate-based validation
- **Fail-Closed Design:** Actions are blocked by default unless authorization can be established and verified

## The Five Tests

| Test | Requirement | Enforced Through |
|------|-------------|------------------|
| **STOP** | System can be halted before side-effects | Effect-token issuance gated by authorization verdict |
| **OWNERSHIP** | Each consequential decision maps to named accountable authority | Policy and runtime attestations preserve accountability and key separation |
| **REPLAY** | Decision can be reproduced at boundary | State-Replay or Protocol-Replay modes |
| **ESCALATION** | Control transfers at defined policy boundaries | Explicit routing to authorized human authority when policy authority is exceeded |
| **PROVENANCE** *(normative; conformance deferred)* | Inputs grounding a verdict have an established origin | Origin, not truth; conformance vectors deferred to a later bundle |

> **5TS v1.2.0** specifies five normative tests. The machine-checkable conformance bundle remains **v1.0.2** and tests four of them; Provenance conformance is not yet assertable and lands in a later bundle once input-origin binding is defined. Existing four-test conformance claims remain valid.

## The Enforcement Triad

A governance system that only warns is a monitoring system. Deterministic governance requires the ability to **stop actions**, not merely flag them. Every decision boundary must resolve to one of three verdicts:

| Verdict | Meaning | Operational Effect |
| --- | --- | --- |
| **ALLOW** | Action authorized under governing policy | Execution may proceed; an effect-token is issued where an external effect is authorized |
| **DENY** | Policy violation identified | Execution halted; no side-effects permitted |
| **ABSTAIN** | Policy cannot resolve the action to ALLOW or DENY | Authority returned; action blocked pending authorized human resolution |

### Why ABSTAIN matters

`ABSTAIN` is the system's explicit acknowledgment of its own epistemic boundaries: a controlled handoff of authority rather than an uncertain guess. Systems that always answer are optimizing for completion. Systems that know when *not* to answer are optimizing for correctness.

**Operational contract:**

- `ABSTAIN` triggers mandatory escalation, routing to an authorized human review queue, policy authority review, or other designated escalation path
- In regulated contexts, `ABSTAIN` is **fail-closed**: the action does not proceed unless and until an authorized party renders a definitive verdict
- `ABSTAIN` is not a soft "maybe"; it is a hard gate that transfers decision authority while preventing unauthorized execution
- Default behavior: `ABSTAIN` blocks execution unless and until an authorized override resolves the held action.

**Schema mapping.** In the v1.0.2 PCD schema, ALLOW maps to `approved`, DENY maps to `denied`, and ABSTAIN maps to `escalated`. The field value `escalated` records an ABSTAIN verdict and its mandatory transfer of authority; ESCALATE is not a verdict.

## Quick Start

*Enable auditors to verify governance decisions through deterministic evidence rather than sampling.*

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

### Inspect an Example PCD

```bash
cat examples/model-deployment-state-replay.json
```

Use this file as the starting point for your own PCD and validate it with the quickstart validator.

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
│   ├── positive/               # Must PASS (3 vectors)
│   │   ├── PCD-A1_state_auto_approve.json
│   │   ├── PCD-A2_protocol_with_gates.json
│   │   └── PCD-A3_fail_closed_denial.json
│   ├── negative/               # Must FAIL with specific errors (5 vectors)
│   │   ├── NC-1_posthoc_signature.json
│   │   ├── NC-2_missing_custody.json
│   │   ├── NC-3_key_separation.json
│   │   ├── NC-4_untyped_lineage.json
│   │   └── NC-5_side_effect_on_denial.json
│   └── MANIFEST.json               # Bundle file hashes and expected results
│
├── tools/                       # Reference implementations
│   ├── validator/              # Quickstart conformance validator
│   │   └── quickstart_validate.py
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

5TS supports diverse AI deployment patterns:

| Profile | PCD Emission | Replay Mode | Key Considerations |
|---------|--------------|-------------|-------------------|
| **LLM Tools** | Per tool action with external effects | State or Protocol | Typed lineage for tool I/O |
| **RAG Systems** | Per response triggering workflows | Protocol (frozen index) | Gates on answerability/attribution |
| **Model Deployment** | At deployment and policy changes | State or Protocol (eval gates) | Pre-exec policy signature required |
| **BPMN/ETL** | Per job with external writes | State or Protocol | Compensating actions for rollbacks |
| **Agentic Systems** | Per plan execution | Protocol with explicit gates | Sub-PCDs for high-risk steps |

## Conformance

To claim conformance to the v1.0.2 conformance bundle (four of the five tests), implementers must:

1. **Pass all test vectors:** 3 positive (PASS), 5 negative (expected failures with correct error codes)
2. **Publish conformance claim:**
   ```
   Tool@Version • PCD-1 • Bundle-1.0.2 • 8/8 • sha256:<bundle_hash> • logs_link
   ```
3. **Implement core verification:** PCD schema validation, signature verification, replay logic, fail-closed enforcement

Provenance conformance, and full five-test conformance, are not yet assertable; see §7.4. See [SPECIFICATION.md](SPECIFICATION.md) §7 for complete conformance requirements.

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
- **Email:** info@ferz.ai
- **Website:** https://ferz.ai

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code of conduct
- How to submit issues and pull requests
- Development workflow
- Testing requirements

## Related Standards & Documents

- **[Deterministic AI Governance - Executive Guide](https://ferz.ai/downloads/deterministic-ai-governance-executive-guide.pdf)** - Business rationale and minimum governance bar
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
| 1.0.3 | 2026-02 | Added Enforcement Triad (ALLOW/DENY/ABSTAIN) with ABSTAIN operational contract |
| 1.2.0 | 2026-06 | Renamed 4TS to 5TS; added Provenance as fifth normative test; Provenance conformance deferred; conformance bundle unchanged at v1.0.2 |

See [CHANGELOG.md](CHANGELOG.md) for detailed changes.

## License

- **Specification Text and Documentation:** [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)
  - Attribution required
  - Non-commercial use
  - No derivatives
  
- **Schemas, Examples, Tools, and Test Vectors:** [MIT License](https://opensource.org/licenses/MIT)
  - Permissive use of the published code (patent rights reserved; see [LICENSE.md](LICENSE.md))

See [LICENSE.md](LICENSE.md) for complete terms.

For commercial licensing inquiries: info@ferz.ai

---

**© 2025–2026 FERZ, Inc.** | Vendor-neutral published standard for verifiable AI governance
