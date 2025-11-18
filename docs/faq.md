# 4TS Frequently Asked Questions (FAQ)

## General Questions

### What is 4TS?

The Four Tests Standard (4TS) is a vendor-neutral technical specification that enables organizations to prove AI systems meet compliance requirements through:
- **Stop-capable** decisions with fail-closed design
- **Owned** decisions with cryptographic signatures
- **Replayable** decisions through state or protocol verification
- **Escalatable** decisions with mandatory custody routes

### Who needs 4TS?

Organizations deploying AI in regulated industries:
- Healthcare (FDA 510(k), EU MDR)
- Financial services (SR 11-7, ECOA, MiFID II)
- Government/defense (NIST AI RMF, DoD principles)
- Any high-stakes environment requiring audit trails

### Is 4TS free to use?

**Yes, with dual licensing:**
- **Schemas/tools:** MIT License (completely free for any use)
- **Specification text:** CC BY-NC-ND 4.0 (free for non-commercial use)

Commercial entities can freely implement 4TS using the MIT-licensed schemas and tools. See [LICENSE.md](../LICENSE.md) for details.

### How is 4TS different from other AI governance frameworks?

| Feature | 4TS | Other Frameworks |
|---------|-----|------------------|
| **Verification** | Mathematical/deterministic | Policy documents |
| **Proof** | Cryptographically signed PCDs | Attestation letters |
| **Replay** | Byte-exact or gate-based | Manual review |
| **Vendor Neutrality** | Open standard | Often proprietary |
| **Enforcement** | Runtime (fail-closed) | Post-hoc audits |

## Technical Questions

### What's the difference between State-Replay and Protocol-Replay?

**State-Replay:**
- Requires byte-exact artifact reproduction
- All steps must be deterministic
- Lower verification cost (just hash checking)
- Best for: Model deployment, ETL pipelines, policy updates

**Protocol-Replay:**
- Allows stochastic steps (sampling, LLM generation)
- Requires deterministic acceptance gates
- Higher verification cost (must re-run gates)
- Best for: RAG systems, agentic workflows, LLM tool chains

### Can I use 4TS with existing MLOps tools?

Yes! 4TS is designed to integrate with existing workflows:

```python
# Example: Wrap MLflow deployment with 4TS
def deploy_with_4ts(model_uri, policy_id):
    # Generate PCD before deployment
    pcd = create_deployment_pcd(
        model_uri=model_uri,
        policy_id=policy_id,
        artifacts=get_model_artifacts(model_uri)
    )
    
    # Verify PCD passes Four Tests
    if validator.validate(pcd):
        # Issue effect-token (approval)
        token = issue_effect_token(pcd)
        
        # Deploy with token
        mlflow.register_model(model_uri, effect_token=token)
    else:
        # Escalate to human review
        escalate_decision(pcd)
```

### How do I handle large models?

Use Merkle trees for chunk-level verification:

```json
{
  "artifacts": {
    "models": [{
      "id": "llama-70b-v2",
      "merkle_root": "9c3f9e8eb8d14e1c...",
      "chunks": [
        {"i": 0, "size": 1048576, "sha256": "e3b0c44..."},
        {"i": 1, "size": 1048576, "sha256": "7f83b16..."}
      ]
    }]
  }
}
```

This allows streaming verification without materializing the entire model.

### What if my pipeline has non-deterministic steps?

Use Protocol-Replay mode with deterministic gates:

```json
{
  "lineage": [
    {
      "id": "step-1-llm-generation",
      "op": "generate_text",
      "stochastic": true  // LLM sampling is non-deterministic
    }
  ],
  "controls": {
    "replay": {"strategy": "protocol"},
    "policy_invariants": {
      "gates": [
        {
          "id": "gate-toxicity",
          "metric": "toxicity_score",
          "dataset": "generated-output",
          "op": "<=",
          "value": 0.1  // Deterministic threshold
        }
      ]
    }
  }
}
```

### How do I implement key role separation?

Use separate key pairs for policy and runtime:

```python
# Policy keys (held by compliance team)
policy_private_key = load_key("policy-key-001.pem")

# Runtime keys (held by automated systems/HSMs)
runtime_private_key = load_key("runtime-key-005.pem")

# Policy signs BEFORE execution
policy_signature = sign(policy_content, policy_private_key)

# Runtime signs PCD AT execution
pcd_signature = sign(canonical_pcd, runtime_private_key)

# Verifier checks:
# 1. Policy signature timestamp < execution timestamp
# 2. Keys don't overlap between roles
```

## Implementation Questions

### Where should I start?

1. **Read** [Quick Start Guide](quickstart.md)
2. **Validate** example PCDs with the reference validator
3. **Create** a minimal PCD for your use case
4. **Integrate** PCD emission into your deployment pipeline
5. **Test** against conformance test vectors

### Do I need to modify my existing models?

No! 4TS operates at the deployment/governance layer:
- Models remain unchanged
- Add PCD emission wrapper around deployment
- Integrate verification into approval workflow

### What about real-time systems?

4TS supports millisecond-scale inference decisions:

**Optimization strategies:**
- Pre-compute policy signatures (valid for effective window)
- Cache artifact hashes
- Use lightweight gates for protocol-replay
- Defer full verification to async audit process
- Issue effect-tokens from fast path after basic checks

Typical overhead: <10ms for inference-boundary PCDs

### How do I handle model retraining?

Create a new deploy-boundary PCD when model changes:

```json
{
  "decision": {
    "id": "deploy-model-v2.0",
    "boundary": "deploy",
    "effective_window": {
      "start": "2025-12-01T00:00:00Z",
      "end": "2026-12-01T00:00:00Z"
    }
  },
  "artifacts": {
    "models": [{
      "id": "model-v2.0",
      "sha256": "new-model-hash..."
    }],
    "policies": [{
      "id": "retraining-policy-2025",
      "sha256": "policy-hash..."
    }]
  }
}
```

## Conformance Questions

### What does conformance mean?

A system is 4TS-conformant if it:
1. Emits valid PCDs according to the schema
2. Enforces all Four Tests
3. Passes all 8 conformance test vectors (3 positive, 5 negative)
4. Publishes conformance claim with verification logs

### How do I claim conformance?

1. **Pass all tests:**
   ```bash
   python tools/validator/quickstart_validate.py --all
   ```

2. **Publish conformance claim:**
   ```
   MyTool@1.0 • PCD-1 • Bundle-1.0.2 • 8/8 • sha256:abc123... • https://example.com/logs
   ```

3. **Make verification logs public**

4. **Update documentation** to reference 4TS conformance

### Can I use 4TS logos/trademarks?

**Permitted without permission:**
- Referencing the standard in documentation
- Claiming conformance (if valid)
- Academic citations

**Requires permission:**
- Using "4TS" in product names
- Implying endorsement by FERZ LLC
- Creating derivative standards

Contact contact@ferzconsulting.com for trademark licensing.

### What about false conformance claims?

False conformance claims may result in:
- Revocation of permission to use 4TS trademarks
- Public correction in GitHub repository
- Potential legal action for fraudulent claims

We monitor conformance claims and request verification logs when published.

## Security Questions

### How secure is 4TS?

Security depends on implementation:

**4TS provides:**
- Cryptographic signatures for authenticity
- Hash-based tampering detection
- Fail-closed design (deny by default)
- Key role separation

**You must provide:**
- Secure key management (HSMs recommended)
- Protected timestamp sources
- Immutable audit log storage
- Network security for PCD transmission

### What signature algorithms are supported?

- EdDSA (recommended for performance)
- ECDSA (widely supported)
- RSA (legacy compatibility)

All must produce deterministic signatures for given inputs.

### How do I protect against replay attacks?

PCDs include timestamps and effective windows:

```json
{
  "decision": {
    "effective_window": {
      "start": "2025-11-01T00:00:00Z",
      "end": "2026-11-01T00:00:00Z"  // Limited validity
    }
  },
  "attestations": {
    "timestamps": {
      "exec_start": "2025-11-01T09:15:00Z"  // Unique per execution
    }
  }
}
```

Verifiers should reject PCDs:
- Outside their effective window
- With duplicate decision IDs
- With timestamps in the future

## Licensing & Commercial Questions

### Can I sell products that use 4TS?

**Yes!** The schemas and tools are MIT-licensed, allowing commercial use without fees.

### Do I need a commercial license?

**Not for implementation.** Commercial licenses are only needed for:
- Using 4TS branding in product names
- Creating derivative specifications
- Offering 4TS conformance as a paid service

### Who owns 4TS?

FERZ LLC is the steward of the 4TS standard, maintaining it as an open, vendor-neutral specification.

### Can I contribute to 4TS?

Yes! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines. Contributions to schemas/tools are MIT-licensed. Specification changes require FERZ approval due to CC BY-NC-ND licensing.

## Getting Help

### Where can I ask questions?

- **Technical questions:** [GitHub Discussions](https://github.com/ferz-ai/4ts-standard/discussions)
- **Bug reports:** [GitHub Issues](https://github.com/ferz-ai/4ts-standard/issues)
- **Email support:** contact@ferzconsulting.com
- **Security issues:** security@ferzconsulting.com (private disclosure)

### Is there commercial support available?

Yes, FERZ LLC offers:
- Implementation consulting
- Custom integration development
- Training and workshops
- Audit and conformance review

Contact contact@ferzconsulting.com for information.

### How can I stay updated?

- **Watch** the [GitHub repository](https://github.com/edmeyman/4ts-standard/)
- **Subscribe** to release notifications
- **Follow** FERZ on [LinkedIn](https://www.linkedin.com/company/ferzllc/)
- **Visit** https://ferz.ai for announcements

---

**Don't see your question?** [Ask in GitHub Discussions](https://github.com/ferz-ai/4ts-standard/discussions) or email contact@ferzconsulting.com

**© 2025 FERZ LLC** | [4TS Standard](https://github.com/ferz-ai/4ts-standard)
