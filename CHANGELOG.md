# Changelog

All notable changes to the Four Tests Standard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Additional language bindings (Go, Rust, TypeScript)
- Performance benchmarks for reference verifier
- Visual PCD explorer tool
- Interactive conformance checker

## [1.0.3] - 2026-02-11

### Added
- **Enforcement Triad** — Normative verdict types (ALLOW, DENY, ABSTAIN) added to README and specification
  - `ALLOW`: Action authorized under governing policy; execution proceeds with effect-token issuance
  - `DENY`: Policy violation identified; execution halted with no side-effects permitted
  - `ABSTAIN`: Insufficient confidence to render a verdict; authority explicitly returned with action blocked pending human resolution
- **ABSTAIN operational contract** — `ABSTAIN` must be treated as `DENY` by default unless an authorized override occurs; triggers mandatory escalation to human-in-the-loop queue or policy authority review
- **Epistemic boundary acknowledgment** — Formal recognition that governance systems must know when *not* to answer, distinguishing completion-optimizing systems from correctness-optimizing systems

### Changed
- Updated README with new "The Enforcement Triad" section between The Four Tests table and Quick Start
- Aligned README verdict semantics with AI Governance Taxonomy v1.5

### Fixed
- Corrected repository URL in documentation from `https://github.com/ferz-ai/4ts-standard` to `https://github.com/edmeyman/4ts-standard`

## [1.0.2] - 2025-11-18

### Added
- **Traceability Matrix** - Complete mapping of Four Tests to PCD fields, verification logic, and error codes (§1.2)
- **Glossary** - Comprehensive definitions of all key terms (page 3)
- **Concrete PCD Examples** - Two complete worked examples in Appendix A:
  - Model deployment using state-replay
  - RAG system using protocol-replay
- **GitHub Repository Structure** - Open-source repository with schemas, test vectors, and reference implementation
- **Implementation Profiles Table** - Expanded profiles for LLM Tools, RAG, MLOps, BPMN/ETL, Agentic, and Data Warehouse use cases (§8.1)
- **Extended Error Catalog** - Added E_PROTOCOL_GATE_FAIL and E_KEY_SEPARATION to error codes (§9.1)

### Changed
- Enhanced §2 (PCD Schema) with more detailed field descriptions
- Improved §4 (Replay Modes) with clearer comparison table
- Expanded §8 (Implementation Guidance) with concrete gate examples
- Updated conformance requirements to reflect Bundle v1.0.2

### Docs
- Added Quick Start Guide (docs/quickstart.md)
- Added Implementation Guide (docs/implementation-guide.md)
- Added FAQ (docs/faq.md)
- Added Error Catalog (docs/error-catalog.md)

## [1.0.1] - 2025-10-15

### Added
- **Adoption Profiles** - Six common deployment patterns with recommended configurations:
  - LLM Tools / Function Calling
  - RAG / Retrieval-Augmented Generation
  - MLOps / Model Deployment
  - BPMN/ETL Pipelines
  - Agentic Orchestration
  - Data Warehouse / SQL Decisions
- **Gate Format Specification** - Formal syntax for protocol-replay gates: `metric(dataset[,group_by]) operator value`
- **Error Code Expansion** - Added 12 error codes with deterministic triggers and recovery mechanisms:
  - E_HASH_MISMATCH
  - E_MISSING_CUSTODY
  - E_PREEXEC_SIGNING
  - E_KEY_SEPARATION
  - E_UNTYPED_LINEAGE
  - E_STEP_REPRO_FAIL
  - E_SIDE_EFFECT_ON_DENIAL
  - E_MISSING_EFFECT_TOKEN
  - E_REPLAY_NONDETERMINISTIC
  - E_COUNTERFACTUAL_NOT_MINIMAL
  - E_POLICY_REF_MISSING
  - E_SIG_INVALID
  - E_SIG_MISSING
- **Counterfactual Specification** - Formal requirements for minimal flip explanations
- **Edge Case Documentation** - Clock skew, mixed canonicalization, streaming effects

### Changed
- Clarified gate evaluation order (sorted by id) in §4.2
- Enhanced key role separation requirements in §5.2
- Improved Merkle tree specification for large artifacts in §6.3
- Updated conformance bundle to v1.0.1 with additional test vectors

### Fixed
- Corrected timestamp ordering requirement notation
- Fixed typo in canonicalization rules
- Clarified must-ignore policy for unknown fields

## [1.0.0] - 2025-09-15

### Added
- **Initial Release** - Complete vendor-neutral specification (§§0-11)
- **Core Four Tests** - STOP, OWNERSHIP, REPLAY, ESCALATION
- **PCD Schema** - JSON Schema (draft 2020-12) for Proof-Carrying Decisions
  - Decision boundaries: deploy | policy | inference
  - Artifacts: models, policies, prompts, config, data
  - Lineage: execution steps with inputs/outputs
  - Controls: policy DSL, fail-closed, replay strategy
  - Attestations: signatures, timestamps, hashes
- **Two Replay Modes**
  - State-Replay: byte-exact artifact reproduction
  - Protocol-Replay: deterministic gate re-evaluation
- **Decision Boundaries** - Temporal and hierarchical scoping (§3)
  - Deploy boundary (months to years)
  - Policy boundary (weeks to months)
  - Inference boundary (milliseconds to minutes)
- **Attestation System** - Cryptographic proof of authority (§5)
  - Key role separation (policy vs runtime)
  - Timestamp ordering enforcement
  - Signature verification
- **Lineage Tracking** - Complete execution trace (§6)
  - Typed steps with inputs/outputs
  - Policy references
  - Content-addressed storage (CAS)
- **Conformance Requirements** - Test vectors and validator (§7)
  - 3 positive test cases
  - 5 negative test cases
  - Conformance claim format
- **Implementation Guidance** - Patterns and best practices (§8)
  - Fail-closed design pattern
  - Gate definition best practices
  - Common deployment scenarios
- **Error Handling** - Deterministic error codes and recovery (§9)
- **Extensions System** - Vendor-specific extensions with must-ignore policy (§10)
- **Reference Implementation** - Python quickstart validator

### Specification Sections
- §0: Introduction and Metadata
- §1: Purpose and Scope
- §2: PCD Schema Specification
- §3: Decision Boundaries
- §4: Replay Modes
- §5: Attestation and Verification
- §6: Lineage and Custody
- §7: Conformance Requirements
- §8: Implementation Guidance
- §9: Error Handling and Recovery
- §10: Extensions and Interoperability
- §11: References and Changelog

### Licensing
- **Specification**: CC BY-NC-ND 4.0
- **Schemas & Vectors**: MIT License

### Conformance Bundle v1.0.0
- pcd.schema.json
- verifier.config.schema.json
- 3 positive test vectors (PCD-A1, A2, A3)
- 5 negative test vectors (NC-1 through NC-5)
- quickstart_validate.py
- ERROR_CATALOG.md
- MANIFEST.json
- README_v1.0.0.md

### Documentation
- Complete technical specification (24 pages)
- Glossary of key terms
- Examples for common use cases
- Normative references (JSON Schema, RFC 3339, SHA-256, EdDSA/ECDSA)

### Support
- GitHub repository: https://github.com/edmeyman/4ts-standard
- Issue tracker for bug reports and feature requests
- Email support: contact@ferzconsulting.com
- Website: https://ferz.ai

## Future Roadmap

### v1.1.0 (Planned Q1 2026)
- Enhanced Merkle tree support for streaming verification
- Additional test vectors for edge cases
- Performance optimization guidelines
- Integration examples with major ML frameworks

### v1.2.0 (Planned Q2 2026)
- Multi-party approval workflows
- Delegation and proxy signing
- Batch PCD verification
- Enhanced counterfactual explanations

### v2.0.0 (Future)
- Breaking changes only if absolutely necessary
- 12-month migration period
- Comprehensive migration tooling
- Backward compatibility layer

## Release Management

### Version Numbering
- **MAJOR.MINOR.PATCH** (Semantic Versioning)
- Major: Breaking changes to PCD schema or verification logic
- Minor: New optional features under must-ignore policy
- Patch: Bug fixes, documentation, non-breaking clarifications

### Release Process
1. Community discussion (GitHub Issues/Discussions)
2. Draft specification changes
3. Update conformance bundle
4. Community review period (2-4 weeks for breaking changes)
5. Final approval by FERZ LLC technical team
6. Publication and announcement

### Support Policy
- Current major version: Fully supported
- Previous major version: Security fixes for 12 months
- Older versions: Community support only

---

**Maintained by:** FERZ Inc.  
**Contact:** contact@ferzconsulting.com  
**Repository:** https://github.com/edmeyman/4ts-standard

For detailed specification changes, see commit history and pull requests.
