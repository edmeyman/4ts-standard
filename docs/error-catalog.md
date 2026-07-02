# 5TS Error Catalog

Complete reference for the deterministic error codes defined in SPECIFICATION.md §9.1. Verifiers must detect, report, and handle these errors deterministically. On any error the PCD is rejected; recovery describes the remediation path.

**Bundle:** v1.0.2 | **Applies to:** Stop, Ownership, Replay, Escalation (the four testable tests)

## Error Codes

### E_HASH_MISMATCH
- **Trigger:** Artifact hash verification fails during replay, or `attestations.canonical_hash` does not match the computed pre-attestation envelope hash (SPECIFICATION.md §5)
- **Test:** Replay
- **Recovery:** Reject PCD, write audit log. Verify the artifact has not been modified and check for canonicalization inconsistencies across components (§9.3).

### E_MISSING_CUSTODY
- **Trigger:** Required artifact hash missing
- **Test:** Replay
- **Recovery:** Reject PCD. Every artifact referenced by a decision must carry a SHA-256 custody hash.
- **Conformance vector:** NC-2

### E_PREEXEC_SIGNING
- **Trigger:** `policy_signed > exec_start` (post-hoc authorization)
- **Test:** Ownership
- **Recovery:** Reject PCD, investigate tampering. Policy must be signed before the execution window opens.
- **Conformance vector:** NC-1

### E_KEY_SEPARATION
- **Trigger:** Policy and runtime key sets overlap
- **Test:** Ownership
- **Recovery:** Reject PCD, fix key configuration. Key role separation prevents single-person policy override.
- **Conformance vector:** NC-3

### E_UNTYPED_LINEAGE
- **Trigger:** Lineage step missing input/output types
- **Test:** Replay
- **Recovery:** Reject PCD, fix lineage emission. Typed steps are required for deterministic reconstruction.
- **Conformance vector:** NC-4

### E_STEP_REPRO_FAIL
- **Trigger:** A protocol-replay step fails to reproduce
- **Test:** Replay
- **Recovery:** Reject PCD, investigate. Check that frozen inputs and deterministic metric implementations are in place.

### E_SIDE_EFFECT_ON_DENIAL
- **Trigger:** Effect-token present on a denial path
- **Test:** Stop
- **Recovery:** Reject PCD, open critical audit. Effect-tokens must not exist on denial paths (§8.3); an escalated outcome blocks execution pending authorized human resolution, so an effect-token on an escalated path is the same violation.
- **Conformance vector:** NC-5

### E_MISSING_EFFECT_TOKEN
- **Trigger:** No effect-token on an approval that authorizes external effects
- **Test:** Stop
- **Recovery:** Reject PCD, fix emission. All external effects require a valid token issued after approval.
- **Note:** The v1.0.2 conformance bundle tests denial-path effect-token violations (NC-5, E_SIDE_EFFECT_ON_DENIAL); missing-token checks depend on whether the PCD marks an external-effect approval.

### E_REPLAY_NONDETERMINISTIC
- **Trigger:** Replay produces a different result across runs
- **Test:** Replay
- **Recovery:** Reject PCD, audit. Identify stochastic steps and either freeze them or move to Protocol-Replay with deterministic gates.

### E_PROTOCOL_GATE_FAIL
- **Trigger:** Gate evaluation fails or is non-deterministic
- **Test:** Replay
- **Recovery:** Reject PCD. Gates must be deterministic, frozen, and explicit (§8.2).

### E_SIG_INVALID
- **Trigger:** Signature verification fails
- **Test:** Ownership
- **Recovery:** Reject PCD, investigate. Confirm key material and canonicalization used at signing time.

### E_SIG_MISSING
- **Trigger:** Required signature missing: `attestations.signatures` is empty, a policy-role or runtime-role signature is absent, or a signature value is empty. The quickstart validator checks presence structurally; cryptographic verification of signature values is E_SIG_INVALID and requires key material
- **Test:** Ownership
- **Recovery:** Reject PCD. Policy and runtime attestations are mandatory PCD components.

## Recovery Principles (§9.2)

- **Immediate rejection:** Do not process the PCD further; emit the error code
- **Immutable logging:** Record the error with full context for audit
- **Escalation:** Route to human custody for critical errors (tampering, key violations)
- **Remediation guidance:** Provide actionable steps to fix underlying issues
- **Monitoring:** Track error rates and patterns for systemic issues

## Edge Cases (§9.3)

- **Clock skew:** Use trusted timestamping or accept small tolerances (for example, ±5 seconds) with audit logging
- **Mixed canonicalization:** Use a single canonical implementation across all components
- **Streaming effects:** Buffer outputs until approval is confirmed; effects before full approval violate fail-closed requirements

---

**© 2025–2026 FERZ, Inc.** | [5TS Standard](https://github.com/edmeyman/4ts-standard)
