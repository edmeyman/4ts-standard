# 4TS Implementation Guide

**Version:** 1.0.2  
**Audience:** AI/ML engineers, platform architects, compliance engineers  
**Prerequisites:** Familiarity with SPECIFICATION.md §§0-11

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Implementation Patterns by Profile](#implementation-patterns-by-profile)
4. [PCD Generation Pipeline](#pcd-generation-pipeline)
5. [Verification Engine Design](#verification-engine-design)
6. [State-Replay Implementation](#state-replay-implementation)
7. [Protocol-Replay Implementation](#protocol-replay-implementation)
8. [Key Management and Attestation](#key-management-and-attestation)
9. [Storage and Retrieval](#storage-and-retrieval)
10. [Integration Patterns](#integration-patterns)
11. [Performance Optimization](#performance-optimization)
12. [Testing and Validation](#testing-and-validation)
13. [Production Deployment](#production-deployment)
14. [Troubleshooting](#troubleshooting)

---

## Introduction

This guide provides detailed implementation patterns for building 4TS-conformant systems. It covers the complete lifecycle from PCD generation through verification, with concrete examples for common deployment scenarios.

### Design Philosophy

4TS implementations follow three core principles:

1. **Fail-closed by design:** Systems deny by default; approval must be proven
2. **Deterministic verification:** Same inputs always produce same verification result
3. **Evidence before effects:** No side effects without cryptographic proof of approval

### Architecture Overview

A minimal 4TS implementation consists of:

- **PCD Emitter:** Generates proof-carrying decisions at decision boundaries
- **Verifier:** Validates PCDs against conformance requirements
- **Artifact Store:** Content-addressed storage for models, policies, data
- **Key Management:** Separate policy and runtime key infrastructure
- **Audit Logger:** Immutable log of all decisions and verification results

---

## Getting Started

### Quickstart: Minimal Implementation

The fastest path to 4TS conformance:

```python
# 1. Install dependencies
pip install pycryptodome jsonschema requests

# 2. Generate your first PCD
from datetime import datetime
import json
import hashlib

def create_minimal_pcd(model_artifact, policy_artifact):
    """Create a minimal state-replay PCD for model deployment."""
    
    pcd = {
        "pcd_spec_version": "1.0.2",
        "decision": {
            "id": f"deploy-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "boundary": "deploy",
            "outcome": "approved",
            "effective_window": {
                "start": datetime.utcnow().isoformat() + "Z"
            },
            "routed": False,
            "replayable": True
        },
        "artifacts": {
            "models": [{
                "id": model_artifact["id"],
                "sha256": hashlib.sha256(
                    model_artifact["bytes"]
                ).hexdigest()
            }],
            "policies": [{
                "id": policy_artifact["id"],
                "sha256": hashlib.sha256(
                    policy_artifact["bytes"]
                ).hexdigest()
            }]
        },
        "lineage": [{
            "id": "step-1-validation",
            "op": "model_validation",
            "types": {
                "inputs": ["model", "policy"],
                "outputs": ["validation_report"]
            },
            "inputs": [model_artifact["id"], policy_artifact["id"]],
            "outputs": ["validation-report-001"],
            "policy_refs": [policy_artifact["id"]],
            "stochastic": False
        }],
        "controls": {
            "fail_closed": True,
            "policy_dsl": "internal-v1",
            "replay": {
                "strategy": "state"
            }
        },
        "attestations": {
            "timestamps": {
                "policy_signed": "2025-01-01T00:00:00Z",
                "exec_start": datetime.utcnow().isoformat() + "Z",
                "exec_end": datetime.utcnow().isoformat() + "Z"
            }
        }
    }
    
    return pcd

# 3. Validate against schema
import jsonschema

with open('schemas/pcd.schema.json') as f:
    schema = json.load(f)

jsonschema.validate(instance=pcd, schema=schema)
print("✓ PCD is valid")
```

### Recommended Implementation Path

1. **Week 1:** Implement PCD emission for your primary decision boundary (usually `deploy`)
2. **Week 2:** Build basic verifier that validates schema and signatures
3. **Week 3:** Implement state-replay or protocol-replay verification
4. **Week 4:** Run conformance tests and publish conformance claim

---

## Implementation Patterns by Profile

### LLM Tool Chains

**Pattern:** Emit PCD per tool invocation with external effects (API calls, database writes, file operations).

**Decision Boundary:** `inference`  
**Replay Mode:** State-Replay (default) or Protocol-Replay  
**Key Considerations:** Typed lineage for tool I/O, explicit effect-token gating

```python
def emit_tool_pcd(tool_name, inputs, outputs, policy_id):
    """Emit PCD for LLM tool execution."""
    
    pcd = {
        "pcd_spec_version": "1.0.2",
        "decision": {
            "id": f"tool-{tool_name}-{uuid.uuid4()}",
            "boundary": "inference",
            "outcome": "approved",  # Only if policy gates pass
            "effective_window": {
                "start": datetime.utcnow().isoformat() + "Z"
            },
            "routed": False,
            "replayable": True
        },
        "artifacts": {
            "prompts": [{
                "id": f"prompt-{tool_name}",
                "sha256": hash_artifact(tool_prompt)
            }]
        },
        "lineage": [{
            "id": "step-1-tool-execution",
            "op": f"tool_{tool_name}",
            "types": {
                "inputs": ["user_input", "tool_config"],
                "outputs": ["tool_result"]
            },
            "inputs": inputs,
            "outputs": outputs,
            "policy_refs": [policy_id],
            "stochastic": False
        }],
        "controls": {
            "fail_closed": True,
            "replay": {"strategy": "state"}
        }
    }
    
    # CRITICAL: Only issue effect-token if approved
    if pcd["decision"]["outcome"] == "approved":
        effect_token = generate_effect_token(pcd)
        return pcd, effect_token
    else:
        return pcd, None
```

### RAG Systems

**Pattern:** Emit PCD per response that triggers workflows or consequential actions.

**Decision Boundary:** `inference`  
**Replay Mode:** Protocol-Replay (frozen index)  
**Key Considerations:** Gates on answerability and attribution scores

```python
def emit_rag_pcd(query, retrieved_docs, response, corpus_hash):
    """Emit protocol-replay PCD for RAG system."""
    
    # Calculate attribution score (deterministic)
    attribution_score = calculate_attribution(response, retrieved_docs)
    
    # Define gates
    gates = [
        {
            "id": "gate-attribution",
            "metric": "attribution_score",
            "dataset": "step-3-validation-output",
            "op": ">=",
            "value": 0.85
        },
        {
            "id": "gate-corpus-frozen",
            "metric": "corpus_hash",
            "dataset": f"corpus-snapshot-{datetime.utcnow().date()}",
            "op": "==",
            "value": corpus_hash
        }
    ]
    
    # Evaluate gates
    gates_pass = all([
        attribution_score >= 0.85,
        verify_corpus_hash(corpus_hash)
    ])
    
    pcd = {
        "pcd_spec_version": "1.0.2",
        "decision": {
            "id": f"rag-{uuid.uuid4()}",
            "boundary": "inference",
            "outcome": "approved" if gates_pass else "denied",
            "effective_window": {
                "start": datetime.utcnow().isoformat() + "Z"
            },
            "routed": False,
            "replayable": True,
            "counterfactual": {
                "flip_var": "gate-attribution-threshold",
                "explanation": f"If attribution < 0.85, would deny (actual: {attribution_score})"
            }
        },
        "lineage": [
            {
                "id": "step-1-retrieval",
                "op": "vector_search",
                "types": {
                    "inputs": ["query", "corpus"],
                    "outputs": ["retrieved_docs"]
                },
                "stochastic": True  # Ranking is stochastic
            },
            {
                "id": "step-2-generation",
                "op": "llm_generate",
                "types": {
                    "inputs": ["retrieved_docs", "prompt"],
                    "outputs": ["response"]
                },
                "stochastic": True
            },
            {
                "id": "step-3-validation",
                "op": "validate_attribution",
                "types": {
                    "inputs": ["response", "retrieved_docs"],
                    "outputs": ["attribution_score"]
                },
                "stochastic": False  # Validation is deterministic
            }
        ],
        "controls": {
            "fail_closed": True,
            "replay": {"strategy": "protocol"},
            "policy_invariants": {"gates": gates}
        }
    }
    
    return pcd
```

### Model Deployment

**Pattern:** Emit PCD at deployment and policy changes.

**Decision Boundary:** `deploy`  
**Replay Mode:** State-Replay or Protocol-Replay (with eval gates)  
**Key Considerations:** Pre-execution policy signature required

```python
def emit_deployment_pcd(model, policy, eval_results):
    """Emit deployment PCD with pre-signed policy."""
    
    # Policy MUST be signed before deployment
    policy_signed_ts = policy["signature"]["timestamp"]
    deployment_start_ts = datetime.utcnow()
    
    if policy_signed_ts > deployment_start_ts:
        raise ValueError("E_PREEXEC_SIGNING: Policy signed after deployment")
    
    pcd = {
        "pcd_spec_version": "1.0.2",
        "decision": {
            "id": f"deploy-{model['id']}",
            "boundary": "deploy",
            "outcome": "approved",
            "effective_window": {
                "start": deployment_start_ts.isoformat() + "Z",
                "end": (deployment_start_ts + timedelta(days=365)).isoformat() + "Z"
            },
            "routed": False,
            "replayable": True
        },
        "artifacts": {
            "models": [{
                "id": model["id"],
                "sha256": model["hash"],
                "merkle_root": model.get("merkle_root")  # For large models
            }],
            "policies": [{
                "id": policy["id"],
                "sha256": policy["hash"]
            }]
        },
        "lineage": [{
            "id": "step-1-evaluation",
            "op": "model_evaluation",
            "types": {
                "inputs": ["model", "test_dataset", "policy"],
                "outputs": ["eval_report"]
            },
            "inputs": [model["id"], eval_results["dataset_id"], policy["id"]],
            "outputs": [eval_results["report_id"]],
            "policy_refs": [policy["id"]],
            "stochastic": False
        }],
        "controls": {
            "fail_closed": True,
            "replay": {"strategy": "state"}
        },
        "attestations": {
            "timestamps": {
                "policy_signed": policy_signed_ts.isoformat() + "Z",
                "exec_start": deployment_start_ts.isoformat() + "Z",
                "exec_end": datetime.utcnow().isoformat() + "Z"
            },
            "signatures": [
                {
                    "key_id": policy["signature"]["key_id"],
                    "algorithm": "EdDSA",
                    "signature": policy["signature"]["value"],
                    "role": "policy"
                }
            ],
            "key_roles": {
                "policy": [policy["signature"]["key_id"]],
                "runtime": [get_runtime_key_id()]
            }
        }
    }
    
    return pcd
```

---

## PCD Generation Pipeline

### Architecture

```
┌─────────────┐
│   Policy    │──┐
│   Engine    │  │
└─────────────┘  │
                 │
┌─────────────┐  │  ┌──────────────┐
│  Execution  │──┼─→│ PCD Builder  │
│   Context   │  │  └──────────────┘
└─────────────┘  │         │
                 │         ▼
┌─────────────┐  │  ┌──────────────┐
│  Artifact   │──┘  │ Attestation  │
│   Store     │     │   Service    │
└─────────────┘     └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  PCD Store   │
                    └──────────────┘
```

### PCD Builder Component

```python
class PCDBuilder:
    """Builds 4TS-conformant PCDs with automatic validation."""
    
    def __init__(self, artifact_store, key_manager, schema_validator):
        self.artifact_store = artifact_store
        self.key_manager = key_manager
        self.schema_validator = schema_validator
    
    def create_pcd(self, decision_context):
        """Create PCD from execution context."""
        
        # 1. Build decision object
        decision = {
            "id": decision_context["decision_id"],
            "boundary": decision_context["boundary"],
            "outcome": decision_context["outcome"],
            "effective_window": decision_context["window"],
            "routed": decision_context.get("routed", False),
            "replayable": True
        }
        
        # 2. Gather artifacts and hash them
        artifacts = self._hash_artifacts(decision_context["artifacts"])
        
        # 3. Build lineage with type information
        lineage = self._build_lineage(decision_context["execution_trace"])
        
        # 4. Extract control policy and gates
        controls = {
            "fail_closed": True,
            "policy_dsl": decision_context.get("policy_dsl", "internal-v1"),
            "replay": {
                "strategy": decision_context.get("replay_strategy", "state")
            }
        }
        
        if controls["replay"]["strategy"] == "protocol":
            controls["policy_invariants"] = {
                "gates": decision_context["gates"]
            }
        
        # 5. Create attestations
        attestations = self._create_attestations(
            decision_context,
            artifacts,
            lineage
        )
        
        # 6. Assemble PCD
        pcd = {
            "pcd_spec_version": "1.0.2",
            "decision": decision,
            "artifacts": artifacts,
            "lineage": lineage,
            "controls": controls,
            "attestations": attestations
        }
        
        # 7. Validate against schema
        self.schema_validator.validate(pcd)
        
        # 8. Add canonical hash
        pcd["attestations"]["canonical_hash"] = self._compute_canonical_hash(pcd)
        
        return pcd
    
    def _hash_artifacts(self, artifacts):
        """Hash all artifacts and store in CAS."""
        hashed = {}
        
        for artifact_type, artifact_list in artifacts.items():
            hashed[artifact_type] = []
            for artifact in artifact_list:
                # Store in content-addressed storage
                artifact_hash = self.artifact_store.store(artifact["bytes"])
                
                hashed[artifact_type].append({
                    "id": artifact["id"],
                    "sha256": artifact_hash
                })
        
        return hashed
    
    def _build_lineage(self, execution_trace):
        """Build typed lineage from execution trace."""
        lineage = []
        
        for step in execution_trace:
            lineage.append({
                "id": step["id"],
                "op": step["operation"],
                "types": {
                    "inputs": step["input_types"],
                    "outputs": step["output_types"]
                },
                "inputs": step["inputs"],
                "outputs": step["outputs"],
                "policy_refs": step.get("policy_refs", []),
                "stochastic": step.get("stochastic", False)
            })
        
        return lineage
    
    def _create_attestations(self, context, artifacts, lineage):
        """Create cryptographic attestations."""
        
        # Verify timestamp ordering
        policy_signed = context["policy_signed_timestamp"]
        exec_start = context["exec_start"]
        exec_end = datetime.utcnow()
        
        if policy_signed > exec_start:
            raise ValueError("E_PREEXEC_SIGNING: Policy signed after execution")
        
        # Get keys with role separation
        policy_key = self.key_manager.get_key("policy")
        runtime_key = self.key_manager.get_key("runtime")
        
        if policy_key["id"] == runtime_key["id"]:
            raise ValueError("E_KEY_SEPARATION: Policy and runtime keys must differ")
        
        return {
            "canonical_hash": "",  # Computed after assembly
            "signatures": [
                {
                    "key_id": policy_key["id"],
                    "algorithm": "EdDSA",
                    "signature": self.key_manager.sign(policy_key, context["policy_hash"]),
                    "role": "policy"
                },
                {
                    "key_id": runtime_key["id"],
                    "algorithm": "EdDSA",
                    "signature": "",  # Signed after canonical hash
                    "role": "runtime"
                }
            ],
            "timestamps": {
                "policy_signed": policy_signed.isoformat() + "Z",
                "exec_start": exec_start.isoformat() + "Z",
                "exec_end": exec_end.isoformat() + "Z"
            },
            "key_roles": {
                "policy": [policy_key["id"]],
                "runtime": [runtime_key["id"]]
            }
        }
    
    def _compute_canonical_hash(self, pcd):
        """Compute deterministic canonical hash of PCD."""
        canonical_json = self._canonicalize(pcd)
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    
    def _canonicalize(self, obj):
        """Produce canonical JSON representation."""
        # Sort keys recursively, normalize numbers, UTF-8 encoding
        return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
```

---

## Verification Engine Design

### Verifier Architecture

```python
class PCDVerifier:
    """Verifies 4TS PCD conformance."""
    
    def __init__(self, schema_validator, artifact_store, key_manager):
        self.schema_validator = schema_validator
        self.artifact_store = artifact_store
        self.key_manager = key_manager
        self.error_logger = ErrorLogger()
    
    def verify(self, pcd):
        """
        Verify PCD conformance.
        Returns (is_valid, errors) tuple.
        """
        errors = []
        
        # Test 1: Schema validation
        try:
            self.schema_validator.validate(pcd)
        except jsonschema.ValidationError as e:
            errors.append({"code": "E_SCHEMA_INVALID", "detail": str(e)})
            return False, errors
        
        # Test 2: STOP - Fail-closed enforcement
        errors.extend(self._verify_stop(pcd))
        
        # Test 3: OWNERSHIP - Key separation and timestamp ordering
        errors.extend(self._verify_ownership(pcd))
        
        # Test 4: REPLAY - State or protocol replay
        errors.extend(self._verify_replay(pcd))
        
        # Test 5: ESCALATION - Custody and routing
        errors.extend(self._verify_escalation(pcd))
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            self.error_logger.log(pcd["decision"]["id"], errors)
        
        return is_valid, errors
    
    def _verify_stop(self, pcd):
        """Verify fail-closed design."""
        errors = []
        
        # Check fail_closed flag
        if not pcd.get("controls", {}).get("fail_closed", False):
            errors.append({
                "code": "E_FAIL_OPEN",
                "detail": "controls.fail_closed must be true"
            })
        
        # Check effect-token on denial
        if pcd["decision"]["outcome"] == "denied":
            # Effect-tokens MUST NOT exist on denial paths
            # (implementation-specific check)
            pass
        
        return errors
    
    def _verify_ownership(self, pcd):
        """Verify ownership through signatures and timestamps."""
        errors = []
        
        attestations = pcd.get("attestations", {})
        timestamps = attestations.get("timestamps", {})
        
        # Verify timestamp ordering
        policy_signed = datetime.fromisoformat(timestamps["policy_signed"].replace('Z', '+00:00'))
        exec_start = datetime.fromisoformat(timestamps["exec_start"].replace('Z', '+00:00'))
        exec_end = datetime.fromisoformat(timestamps["exec_end"].replace('Z', '+00:00'))
        
        if policy_signed > exec_start:
            errors.append({
                "code": "E_PREEXEC_SIGNING",
                "detail": f"Policy signed ({policy_signed}) after execution started ({exec_start})"
            })
        
        if exec_start > exec_end:
            errors.append({
                "code": "E_TIMESTAMP_ORDER",
                "detail": "exec_start must be <= exec_end"
            })
        
        # Verify key role separation
        key_roles = attestations.get("key_roles", {})
        policy_keys = set(key_roles.get("policy", []))
        runtime_keys = set(key_roles.get("runtime", []))
        
        overlap = policy_keys & runtime_keys
        if overlap:
            errors.append({
                "code": "E_KEY_SEPARATION",
                "detail": f"Policy and runtime keys overlap: {overlap}"
            })
        
        # Verify signatures
        for sig in attestations.get("signatures", []):
            is_valid = self.key_manager.verify(
                sig["key_id"],
                attestations["canonical_hash"],
                sig["signature"]
            )
            if not is_valid:
                errors.append({
                    "code": "E_SIG_INVALID",
                    "detail": f"Invalid signature for key {sig['key_id']}"
                })
        
        return errors
    
    def _verify_replay(self, pcd):
        """Verify replay capability."""
        errors = []
        
        replay_strategy = pcd.get("controls", {}).get("replay", {}).get("strategy")
        
        if replay_strategy == "state":
            errors.extend(self._verify_state_replay(pcd))
        elif replay_strategy == "protocol":
            errors.extend(self._verify_protocol_replay(pcd))
        else:
            errors.append({
                "code": "E_REPLAY_STRATEGY_UNKNOWN",
                "detail": f"Unknown replay strategy: {replay_strategy}"
            })
        
        return errors
    
    def _verify_state_replay(self, pcd):
        """Verify state-replay: byte-exact artifact reproduction."""
        errors = []
        
        # Verify all artifact hashes
        for artifact_type, artifacts in pcd.get("artifacts", {}).items():
            for artifact in artifacts:
                # Retrieve artifact from CAS
                stored_artifact = self.artifact_store.retrieve(artifact["sha256"])
                
                if stored_artifact is None:
                    errors.append({
                        "code": "E_MISSING_CUSTODY",
                        "detail": f"Artifact {artifact['id']} not found in CAS"
                    })
                    continue
                
                # Verify hash
                actual_hash = hashlib.sha256(stored_artifact).hexdigest()
                if actual_hash != artifact["sha256"]:
                    errors.append({
                        "code": "E_HASH_MISMATCH",
                        "detail": f"Hash mismatch for {artifact['id']}"
                    })
        
        return errors
    
    def _verify_protocol_replay(self, pcd):
        """Verify protocol-replay: gate re-evaluation."""
        errors = []
        
        gates = pcd.get("controls", {}).get("policy_invariants", {}).get("gates", [])
        
        if not gates:
            errors.append({
                "code": "E_PROTOCOL_NO_GATES",
                "detail": "Protocol-replay requires explicit gates"
            })
            return errors
        
        # Re-evaluate each gate
        for gate in gates:
            try:
                gate_result = self._evaluate_gate(gate, pcd)
                if not gate_result:
                    errors.append({
                        "code": "E_PROTOCOL_GATE_FAIL",
                        "detail": f"Gate {gate['id']} failed re-evaluation"
                    })
            except Exception as e:
                errors.append({
                    "code": "E_GATE_EVAL_ERROR",
                    "detail": f"Gate {gate['id']} evaluation error: {str(e)}"
                })
        
        return errors
    
    def _evaluate_gate(self, gate, pcd):
        """
        Evaluate a single gate deterministically.
        
        Gate format: metric(dataset[,group_by]) operator value
        """
        metric = gate["metric"]
        dataset = gate["dataset"]
        operator = gate["op"]
        threshold = gate["value"]
        
        # Retrieve frozen dataset
        dataset_artifact = self.artifact_store.retrieve_by_id(dataset)
        
        # Compute metric deterministically
        actual_value = self._compute_metric(metric, dataset_artifact)
        
        # Evaluate operator
        if operator == ">=":
            return actual_value >= threshold
        elif operator == "<=":
            return actual_value <= threshold
        elif operator == "==":
            return actual_value == threshold
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def _verify_escalation(self, pcd):
        """Verify escalation and custody tracking."""
        errors = []
        
        # Verify typed lineage
        for step in pcd.get("lineage", []):
            if "types" not in step:
                errors.append({
                    "code": "E_UNTYPED_LINEAGE",
                    "detail": f"Step {step['id']} missing type information"
                })
            
            if "policy_refs" not in step or not step["policy_refs"]:
                errors.append({
                    "code": "E_POLICY_REF_MISSING",
                    "detail": f"Step {step['id']} missing policy references"
                })
        
        # Verify custody on denial
        if pcd["decision"]["outcome"] == "denied":
            if not pcd["decision"].get("routed", False):
                errors.append({
                    "code": "E_MISSING_CUSTODY",
                    "detail": "Denied decisions must route to custody"
                })
        
        return errors
```

---

## State-Replay Implementation

### Artifact Hashing

```python
class ArtifactHasher:
    """Deterministic artifact hashing."""
    
    @staticmethod
    def hash_artifact(artifact_bytes):
        """Hash artifact with SHA-256."""
        return hashlib.sha256(artifact_bytes).hexdigest()
    
    @staticmethod
    def hash_large_artifact(artifact_path, chunk_size=1024*1024):
        """
        Hash large artifact with Merkle tree.
        Returns (merkle_root, chunks).
        """
        chunks = []
        chunk_hashes = []
        
        with open(artifact_path, 'rb') as f:
            i = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                chunk_hash = hashlib.sha256(chunk).hexdigest()
                chunks.append({
                    "i": i,
                    "size": len(chunk),
                    "sha256": chunk_hash
                })
                chunk_hashes.append(chunk_hash)
                i += 1
        
        # Compute Merkle root
        merkle_root = ArtifactHasher._compute_merkle_root(chunk_hashes)
        
        return merkle_root, chunks
    
    @staticmethod
    def _compute_merkle_root(hashes):
        """Compute Merkle tree root from leaf hashes."""
        if len(hashes) == 0:
            return hashlib.sha256(b'').hexdigest()
        
        if len(hashes) == 1:
            return hashes[0]
        
        # Build tree bottom-up
        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                left = hashes[i]
                right = hashes[i+1] if i+1 < len(hashes) else left
                
                combined = left + right
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            
            hashes = next_level
        
        return hashes[0]
```

### State-Replay Verification

```python
def verify_state_replay(pcd, artifact_store):
    """
    Verify state-replay by reproducing artifacts and comparing hashes.
    """
    
    # 1. Retrieve all artifacts from CAS
    for artifact_type, artifacts in pcd["artifacts"].items():
        for artifact in artifacts:
            stored_bytes = artifact_store.retrieve(artifact["sha256"])
            
            if stored_bytes is None:
                raise ValueError(f"E_MISSING_CUSTODY: {artifact['id']}")
            
            # 2. Verify hash
            actual_hash = hashlib.sha256(stored_bytes).hexdigest()
            if actual_hash != artifact["sha256"]:
                raise ValueError(f"E_HASH_MISMATCH: {artifact['id']}")
    
    # 3. Replay lineage
    for step in pcd["lineage"]:
        if step["stochastic"]:
            raise ValueError(f"E_STEP_STOCHASTIC: State-replay requires deterministic steps")
        
        # Retrieve inputs
        inputs = [artifact_store.retrieve_by_id(inp) for inp in step["inputs"]]
        
        # Re-execute operation
        outputs = execute_operation(step["op"], inputs)
        
        # Verify outputs match
        for i, output_id in enumerate(step["outputs"]):
            expected_output = artifact_store.retrieve_by_id(output_id)
            if outputs[i] != expected_output:
                raise ValueError(f"E_STEP_REPRO_FAIL: {step['id']}")
    
    # 4. Verify canonical hash
    canonical_hash = compute_canonical_hash(pcd)
    if canonical_hash != pcd["attestations"]["canonical_hash"]:
        raise ValueError("E_CANONICAL_HASH_MISMATCH")
    
    return True
```

---

## Protocol-Replay Implementation

### Gate Evaluation Engine

```python
class GateEvaluator:
    """Evaluates deterministic gates on frozen datasets."""
    
    def __init__(self, artifact_store):
        self.artifact_store = artifact_store
        self.metrics = {
            "accuracy": self._compute_accuracy,
            "precision": self._compute_precision,
            "recall": self._compute_recall,
            "attribution_score": self._compute_attribution,
            "corpus_hash": self._verify_corpus_hash,
            "auroc": self._compute_auroc,
            "calibration_error": self._compute_calibration_error,
            "demographic_parity": self._compute_demographic_parity
        }
    
    def evaluate_gates(self, gates, pcd):
        """Evaluate all gates and return pass/fail."""
        results = []
        
        for gate in gates:
            result = self.evaluate_gate(gate, pcd)
            results.append({
                "gate_id": gate["id"],
                "passed": result,
                "gate": gate
            })
        
        all_passed = all(r["passed"] for r in results)
        return all_passed, results
    
    def evaluate_gate(self, gate, pcd):
        """Evaluate single gate."""
        
        # Extract gate parameters
        metric_name = gate["metric"]
        dataset_id = gate["dataset"]
        operator = gate["op"]
        threshold = gate["value"]
        group_by = gate.get("group_by")
        
        # Retrieve frozen dataset
        dataset = self.artifact_store.retrieve_by_id(dataset_id)
        
        # Compute metric
        metric_func = self.metrics.get(metric_name)
        if metric_func is None:
            raise ValueError(f"Unknown metric: {metric_name}")
        
        actual_value = metric_func(dataset, group_by)
        
        # Evaluate operator
        if operator == ">=":
            return actual_value >= threshold
        elif operator == "<=":
            return actual_value <= threshold
        elif operator == "==":
            return actual_value == threshold
        elif operator == ">":
            return actual_value > threshold
        elif operator == "<":
            return actual_value < threshold
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def _compute_accuracy(self, dataset, group_by=None):
        """Compute accuracy on frozen dataset."""
        predictions = dataset["predictions"]
        labels = dataset["labels"]
        
        if group_by:
            # Compute per-group accuracy
            groups = dataset[group_by]
            return self._compute_grouped_metric(
                predictions, labels, groups, self._accuracy
            )
        
        correct = sum(p == l for p, l in zip(predictions, labels))
        return correct / len(predictions)
    
    def _compute_attribution(self, dataset, group_by=None):
        """Compute attribution score (response grounded in sources)."""
        response = dataset["response"]
        sources = dataset["sources"]
        
        # Simple overlap metric (production should use more sophisticated method)
        response_tokens = set(response.lower().split())
        source_tokens = set()
        for source in sources:
            source_tokens.update(source.lower().split())
        
        overlap = len(response_tokens & source_tokens)
        return overlap / len(response_tokens) if response_tokens else 0.0
    
    def _verify_corpus_hash(self, dataset, group_by=None):
        """Verify corpus hash hasn't changed."""
        corpus_bytes = dataset["corpus_bytes"]
        return hashlib.sha256(corpus_bytes).hexdigest()
```

---

## Key Management and Attestation

### Key Separation Pattern

```python
class KeyManager:
    """Manages policy and runtime keys with role separation."""
    
    def __init__(self, hsm_client=None):
        self.hsm_client = hsm_client  # Optional HSM for production
        self.keys = {}
    
    def generate_key_pair(self, role, algorithm="EdDSA"):
        """Generate key pair for specific role."""
        
        if role not in ["policy", "runtime", "approver"]:
            raise ValueError(f"Invalid role: {role}")
        
        if self.hsm_client:
            # Use HSM for production
            key_id = self.hsm_client.generate_key(algorithm, role)
        else:
            # Use software keys for development
            from cryptography.hazmat.primitives.asymmetric import ed25519
            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            key_id = f"{role}-{uuid.uuid4()}"
            self.keys[key_id] = {
                "role": role,
                "algorithm": algorithm,
                "private_key": private_key,
                "public_key": public_key
            }
        
        return key_id
    
    def sign(self, key_id, message):
        """Sign message with specified key."""
        
        key = self.keys.get(key_id)
        if key is None:
            raise ValueError(f"Key not found: {key_id}")
        
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        signature = key["private_key"].sign(message)
        return base64.b64encode(signature).decode('utf-8')
    
    def verify(self, key_id, message, signature):
        """Verify signature with specified key."""
        
        key = self.keys.get(key_id)
        if key is None:
            raise ValueError(f"Key not found: {key_id}")
        
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        signature_bytes = base64.b64decode(signature)
        
        try:
            key["public_key"].verify(signature_bytes, message)
            return True
        except Exception:
            return False
    
    def enforce_role_separation(self, policy_key_id, runtime_key_id):
        """Verify policy and runtime keys are different."""
        
        if policy_key_id == runtime_key_id:
            raise ValueError("E_KEY_SEPARATION: Policy and runtime keys must differ")
        
        policy_key = self.keys.get(policy_key_id)
        runtime_key = self.keys.get(runtime_key_id)
        
        if policy_key["role"] != "policy":
            raise ValueError(f"Key {policy_key_id} is not a policy key")
        
        if runtime_key["role"] != "runtime":
            raise ValueError(f"Key {runtime_key_id} is not a runtime key")
        
        return True
```

---

## Storage and Retrieval

### Content-Addressed Storage

```python
class ContentAddressedStore:
    """Content-addressed storage for immutable artifacts."""
    
    def __init__(self, backend="filesystem", base_path="/var/4ts/artifacts"):
        self.backend = backend
        self.base_path = base_path
        self.index = {}  # id -> hash mapping
    
    def store(self, artifact_bytes, artifact_id=None):
        """
        Store artifact and return SHA-256 hash.
        Artifacts are deduplicated by hash.
        """
        
        # Compute hash
        artifact_hash = hashlib.sha256(artifact_bytes).hexdigest()
        
        # Store indexed by hash
        storage_path = self._hash_to_path(artifact_hash)
        
        if not os.path.exists(storage_path):
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            with open(storage_path, 'wb') as f:
                f.write(artifact_bytes)
        
        # Maintain id -> hash index
        if artifact_id:
            self.index[artifact_id] = artifact_hash
        
        return artifact_hash
    
    def retrieve(self, artifact_hash):
        """Retrieve artifact by hash."""
        
        storage_path = self._hash_to_path(artifact_hash)
        
        if not os.path.exists(storage_path):
            return None
        
        with open(storage_path, 'rb') as f:
            return f.read()
    
    def retrieve_by_id(self, artifact_id):
        """Retrieve artifact by ID (uses index)."""
        
        artifact_hash = self.index.get(artifact_id)
        if artifact_hash is None:
            return None
        
        return self.retrieve(artifact_hash)
    
    def _hash_to_path(self, artifact_hash):
        """Convert hash to filesystem path for sharding."""
        # Use first 4 chars for sharding
        return os.path.join(
            self.base_path,
            artifact_hash[:2],
            artifact_hash[2:4],
            artifact_hash
        )
```

---

## Integration Patterns

### Middleware Integration

```python
class PCDMiddleware:
    """WSGI/ASGI middleware for automatic PCD generation."""
    
    def __init__(self, app, pcd_emitter, policy_engine):
        self.app = app
        self.pcd_emitter = pcd_emitter
        self.policy_engine = policy_engine
    
    async def __call__(self, scope, receive, send):
        """Intercept requests and emit PCDs for consequential actions."""
        
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        # Check if this endpoint requires PCD
        path = scope["path"]
        if not self._requires_pcd(path):
            return await self.app(scope, receive, send)
        
        # Capture request context
        request_context = await self._capture_context(scope, receive)
        
        # Evaluate policy
        policy_decision = self.policy_engine.evaluate(request_context)
        
        if policy_decision["outcome"] != "approved":
            # Deny request
            return await self._send_denial(send, policy_decision)
        
        # Execute request
        response_context = await self.app(scope, receive, send)
        
        # Emit PCD
        pcd = self.pcd_emitter.emit({
            "request": request_context,
            "response": response_context,
            "policy": policy_decision
        })
        
        # Attach PCD to response headers
        await self._attach_pcd_header(send, pcd)
        
        return response_context
    
    def _requires_pcd(self, path):
        """Determine if path requires PCD emission."""
        # Implementation-specific
        return path.startswith("/api/")
```

---

## Performance Optimization

### Caching Strategy

```python
class PCDVerificationCache:
    """Cache verified PCDs to avoid redundant verification."""
    
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, pcd_hash):
        """Get cached verification result."""
        
        entry = self.cache.get(pcd_hash)
        if entry is None:
            return None
        
        # Check TTL
        if time.time() - entry["timestamp"] > self.ttl:
            del self.cache[pcd_hash]
            return None
        
        return entry["result"]
    
    def put(self, pcd_hash, result):
        """Cache verification result."""
        
        self.cache[pcd_hash] = {
            "result": result,
            "timestamp": time.time()
        }
    
    def invalidate(self, pcd_hash):
        """Invalidate cached result."""
        if pcd_hash in self.cache:
            del self.cache[pcd_hash]
```

### Parallel Verification

```python
import concurrent.futures

def verify_batch(pcds, verifier, max_workers=4):
    """Verify multiple PCDs in parallel."""
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(verifier.verify, pcd): pcd for pcd in pcds}
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            pcd = futures[future]
            try:
                is_valid, errors = future.result()
                results.append({
                    "pcd_id": pcd["decision"]["id"],
                    "valid": is_valid,
                    "errors": errors
                })
            except Exception as e:
                results.append({
                    "pcd_id": pcd["decision"]["id"],
                    "valid": False,
                    "errors": [{"code": "E_VERIFICATION_ERROR", "detail": str(e)}]
                })
        
        return results
```

---

## Testing and Validation

### Conformance Testing

```python
import pytest

def test_conformance_vectors():
    """Test against official conformance vectors."""
    
    verifier = PCDVerifier(schema_validator, artifact_store, key_manager)
    
    # Positive vectors - must PASS
    positive_vectors = [
        "test-vectors/positive/PCD-A1_state_auto_approve.json",
        "test-vectors/positive/PCD-A2_protocol_with_gates.json",
        "test-vectors/positive/PCD-A3_fail_closed_denial.json"
    ]
    
    for vector_path in positive_vectors:
        with open(vector_path) as f:
            pcd = json.load(f)
        
        is_valid, errors = verifier.verify(pcd)
        assert is_valid, f"Positive vector {vector_path} failed: {errors}"
    
    # Negative vectors - must FAIL with specific error codes
    negative_vectors = [
        ("test-vectors/negative/NC-1_posthoc_signature.json", "E_PREEXEC_SIGNING"),
        ("test-vectors/negative/NC-2_missing_custody.json", "E_MISSING_CUSTODY"),
        ("test-vectors/negative/NC-3_untyped_lineage.json", "E_UNTYPED_LINEAGE"),
        ("test-vectors/negative/NC-4_side_effect_on_denial.json", "E_SIDE_EFFECT_ON_DENIAL"),
        ("test-vectors/negative/NC-5_protocol_gate_fail.json", "E_PROTOCOL_GATE_FAIL")
    ]
    
    for vector_path, expected_error in negative_vectors:
        with open(vector_path) as f:
            pcd = json.load(f)
        
        is_valid, errors = verifier.verify(pcd)
        assert not is_valid, f"Negative vector {vector_path} should fail"
        
        error_codes = [e["code"] for e in errors]
        assert expected_error in error_codes, \
            f"Expected {expected_error}, got {error_codes}"

def test_publish_conformance_claim():
    """Generate conformance claim after passing tests."""
    
    tool_name = "MyVerifier"
    tool_version = "1.0.0"
    pcd_major = "1"
    bundle_version = "1.0.2"
    
    # Run all test vectors
    test_conformance_vectors()
    
    # Compute manifest hash
    manifest = compute_test_manifest()
    manifest_hash = hashlib.sha256(json.dumps(manifest).encode()).hexdigest()
    
    # Publish conformance claim
    claim = f"{tool_name}@{tool_version} • PCD-{pcd_major} • Bundle-{bundle_version} • 8/8 • sha256:{manifest_hash[:16]}... • https://example.com/4ts/logs"
    
    print(f"Conformance Claim: {claim}")
    
    return claim
```

---

## Production Deployment

### Deployment Checklist

- [ ] **Key Management:** HSM-backed keys with role separation
- [ ] **Storage:** Replicated content-addressed storage with backup
- [ ] **Audit Logging:** Immutable append-only audit trail
- [ ] **Monitoring:** Verification failure rate, latency, error patterns
- [ ] **Schema Validation:** All PCDs validated before storage
- [ ] **Conformance Testing:** Pass all 8 test vectors
- [ ] **Documentation:** Published conformance claim
- [ ] **Disaster Recovery:** Documented recovery procedures

### Production Configuration Example

```yaml
# config/production.yaml

pcd_emitter:
  version: "1.0.2"
  fail_closed: true
  default_replay_strategy: "state"

key_management:
  hsm:
    enabled: true
    provider: "aws-kms"
    region: "us-east-1"
  policy_keys:
    - key_id: "arn:aws:kms:us-east-1:123456789:key/policy-key-1"
      role: "policy"
  runtime_keys:
    - key_id: "arn:aws:kms:us-east-1:123456789:key/runtime-key-1"
      role: "runtime"

storage:
  backend: "s3"
  bucket: "4ts-artifacts-prod"
  replication: true
  backup_schedule: "daily"

verification:
  cache_ttl_seconds: 3600
  max_workers: 8
  timeout_seconds: 30

audit_logging:
  backend: "cloudwatch"
  log_group: "/4ts/audit"
  retention_days: 2555  # 7 years

monitoring:
  metrics_backend: "prometheus"
  alert_on_verification_failure: true
  alert_threshold_percent: 5.0
```

---

## Troubleshooting

### Common Issues

**Issue:** `E_PREEXEC_SIGNING` error  
**Cause:** Policy signed after execution started  
**Fix:** Ensure policy signature timestamp precedes execution start timestamp. Check clock sync across systems.

**Issue:** `E_KEY_SEPARATION` error  
**Cause:** Policy and runtime keys are the same  
**Fix:** Generate separate key pairs for policy and runtime roles.

**Issue:** `E_HASH_MISMATCH` error  
**Cause:** Artifact hash doesn't match stored artifact  
**Fix:** Verify artifact hasn't been modified. Check for canonicalization issues.

**Issue:** `E_PROTOCOL_GATE_FAIL` error  
**Cause:** Gate evaluation failed during protocol-replay  
**Fix:** Verify frozen datasets are truly frozen. Check metric computation is deterministic.

**Issue:** `E_MISSING_CUSTODY` error  
**Cause:** Required artifact not found in CAS  
**Fix:** Ensure all artifacts are stored before PCD emission. Check CAS replication.

### Debug Mode

```python
class DebugPCDVerifier(PCDVerifier):
    """Verifier with detailed debug output."""
    
    def verify(self, pcd, debug=True):
        """Verify with debug logging."""
        
        if debug:
            print(f"\n=== Verifying PCD: {pcd['decision']['id']} ===")
            print(f"Boundary: {pcd['decision']['boundary']}")
            print(f"Outcome: {pcd['decision']['outcome']}")
            print(f"Replay Strategy: {pcd['controls']['replay']['strategy']}")
        
        is_valid, errors = super().verify(pcd)
        
        if debug:
            if is_valid:
                print("✓ PCD VALID")
            else:
                print("✗ PCD INVALID")
                for error in errors:
                    print(f"  - {error['code']}: {error['detail']}")
        
        return is_valid, errors
```

---

## Additional Resources

- **4TS Technical Specification:** [SPECIFICATION.md](../SPECIFICATION.md)
- **Quick Start Guide:** [quickstart.md](quickstart.md)
- **FAQ:** [faq.md](faq.md)
- **Error Catalog:** [error-catalog.md](error-catalog.md)
- **GitHub Repository:** https://github.com/edmeyman/4ts-standard
- **FERZ Website:** https://ferz.ai

---

## Contact and Support

**Technical Questions:** GitHub Issues at https://github.com/edmeyman/4ts-standard/issues  
**Email:** contact@ferzconsulting.com  
**Discussions:** GitHub Discussions at https://github.com/edmeyman/4ts-standard/discussions

---

© 2025 FERZ LLC. This implementation guide is licensed under CC BY-NC-ND 4.0.
