# Nesira Phase 2 Runner Action Class Taxonomy

## Status

```text
DOCUMENT_TYPE: RESEARCH -- RUNNER ACTION CLASS TAXONOMY
PHASE: PHASE_2_RUNNER_ACTION_CLASS_TAXONOMY_GATE
SCOPE: TAXONOMY_ONLY

AUTHORIZES:
runner action-class taxonomy
ineligible action-class list
candidate future action-class vocabulary
future side-effect-budget requirements

RUNNER_IMPLEMENTATION: NOT_AUTHORIZED
SUBPROCESS_EXECUTION: NOT_AUTHORIZED
FILESYSTEM_MUTATION: NOT_AUTHORIZED
NETWORK_EXECUTION: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
CLI_FLAG_CHANGE: NOT_AUTHORIZED
PUBLIC_CLI_EXPOSURE: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE_CHANGE: NOT_AUTHORIZED
COMBINED_VERDICT_BEHAVIOR_CHANGE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLIC_CLAIM_EXPANSION: NOT_AUTHORIZED
```

This taxonomy names which action classes are categorically ineligible and which
classes may be considered by later docs-only gates. It does not authorize any
runner implementation.

## Core Lock

```text
AUTHORIZED_RUNNER_ACTION_CLASSES_NOW = []
```

No action class is authorized for implementation by this document.

The purpose of this taxonomy is to prevent a future runner from becoming a
generic execution surface.

## Classification Vocabulary

Every proposed runner action class must be classified as exactly one:

```text
INELIGIBLE_ALWAYS
CANDIDATE_FOR_FUTURE_MODEL_ONLY
AUTHORIZED_NOW
```

For this document:

```text
AUTHORIZED_NOW is empty.
```

`CANDIDATE_FOR_FUTURE_MODEL_ONLY` means only that a later gate may write a
model for that class. It does not permit code.

## Ineligible Always

The following action classes are forbidden:

```text
GENERIC_SHELL_COMMAND
GENERIC_SUBPROCESS
GENERIC_SCRIPT_RUNNER
GENERIC_PYTHON_MODULE_RUNNER
GENERIC_FILESYSTEM_MUTATOR
GENERIC_NETWORK_CLIENT
ARBITRARY_COMMAND_EXECUTOR
ARBITRARY_PATH_WRITE
ARBITRARY_PATH_DELETE
ARBITRARY_NETWORK_TARGET
LIVE_ISOLATION_RUNNER
SEVERANCE_EXECUTOR
AUTOMATIC_REMEDIATOR
SECRET_EXFILTRATION_PRONE_ACTION
UNBOUNDED_CLEANUP_ACTION
SELF_MODIFYING_RUNNER
```

Any future proposal containing one of these must stop with:

```text
RUNNER_ACTION_CLASS_INELIGIBLE
```

## Ineligible Stability Rule

`INELIGIBLE_ALWAYS` is a stability class, not a temporary label.

Reclassifying any `INELIGIBLE_ALWAYS` action class to
`CANDIDATE_FOR_FUTURE_MODEL_ONLY` or `AUTHORIZED_NOW` requires:

```text
SCOPE_REVISION_REQUIRED
new taxonomy version
explicit rationale
adversarial review
human go/no-go owner approval
```

The following action classes are permanently non-reclassifiable:

```text
LIVE_ISOLATION_RUNNER
SEVERANCE_EXECUTOR
AUTOMATIC_REMEDIATOR
SECRET_EXFILTRATION_PRONE_ACTION
SELF_MODIFYING_RUNNER
```

They must not be moved out of `INELIGIBLE_ALWAYS` by any later Phase 2 runner
gate.

## Candidate Classes For Future Models Only

These classes may be modeled later, but are not authorized now:

```text
AUDIT_RECORD_APPEND_ONLY
  purpose: append a bounded non-secret audit record to a declared audit sink
  required future model: append-only sink, schema, max size, failure semantics

LOCAL_STATUS_MARKER_CREATE_ONLY
  purpose: create a bounded non-secret status marker under a declared output root
  required future model: declared root, fixed filename policy, no overwrite, max size

MANUAL_REVIEW_PACKET_MATERIALIZE_ONLY
  purpose: materialize a bounded packet for human review, not execution
  required future model: declared output root, no executable content, no secrets

ROLLBACK_ABORT_SIGNAL_REQUEST_ONLY
  purpose: request a rollback or abort through a declared non-generic channel
  required future model: channel root, exact payload schema, idempotency, audit
```

These are candidates because they can be described without arbitrary command,
arbitrary path, or arbitrary network parameters. They still require future
per-class authorization before any implementation.

## Candidate Class Requirements

Every future candidate model must define:

```text
class id
version
purpose
explicit non-goals
declared roots
allowed inputs
forbidden inputs
side-effect budget
target scope
maximum payload size
secret-handling rule
idempotency rule
rollback or abort relation
audit record schema
failure semantics
post-action verification boundary
public claim boundary
```

If any field is missing:

```text
ACTION_CLASS_MODEL_INCOMPLETE
```

## Side-Effect Budget Floor

Default side-effect budget:

```text
side_effect_budget = 0
```

A candidate model may request a non-zero budget only by naming the exact effect:

```text
append one audit record
create one marker file under declared root
materialize one review packet under declared root
send one typed rollback/abort request through declared channel
```

Forbidden budget shapes:

```text
write arbitrary file
delete arbitrary file
execute arbitrary process
open arbitrary network connection
mutate unspecified state
cleanup whatever is needed
retry until success
```

## Path And Network Rules

No future class may accept arbitrary paths or arbitrary network targets.

Allowed future path shape, if separately authorized:

```text
declared_root_id@version
fixed relative name from class schema
no traversal
no absolute path from user input
no overwrite unless class explicitly allows it
max byte size
```

Allowed future network shape, if separately authorized:

```text
declared_channel_root_id@version
fixed endpoint or endpoint identity from declared root
typed payload schema
idempotency key
timeout
no arbitrary URL from user input
```

## Executable Content Rule

Candidate classes must not materialize executable instructions.

Forbidden content:

```text
shell command
PowerShell command
bash command
python -m instruction
runbook
copy-paste execution step
script body
```

If a review packet or audit record needs to describe a future action, it must
use declarative fields and must not provide operational instructions.

## Runner / TCB Rule

Every future action class must preserve:

```text
EA-TCB-03
```

The trusted verifier must compare the human-approved context to the
runner-intended context for that specific action class. The runner must not
compute and trust its own binding.

## Human Go And Operator Rule

No action class may be invoked by human go alone.

A future class must require:

```text
authenticated human go
execution authorization evaluator sufficient
operator initiation
trusted verifier match
rollback or abort availability
audit record start
```

Even then, implementation remains blocked until a later per-class runner gate.

## Required Future Negative Cases

Every future action-class model must require tests:

```text
1. class absent from allowlist -> no invocation.
2. class marked INELIGIBLE_ALWAYS -> no invocation.
3. arbitrary command parameter -> rejected.
4. arbitrary path parameter -> rejected.
5. arbitrary network target -> rejected.
6. executable content in review packet -> rejected.
7. missing declared root -> no invocation.
8. missing human go -> no invocation.
9. missing operator initiation -> no invocation.
10. runner-intended context mismatch -> no invocation.
11. rollback or abort unavailable -> no invocation.
12. partial failure does not claim success.
```

## Stop Conditions

Stop with `SCOPE_REVISION_REQUIRED` if a later design:

```text
adds an AUTHORIZED_NOW class without separate authorization
reclassifies an INELIGIBLE_ALWAYS class without taxonomy version and review
reclassifies a permanently non-reclassifiable class
adds a generic command abstraction
permits arbitrary path or URL input
permits executable content in output
collapses trusted verifier and runner
collapses human go and operator initiation
omits side-effect budget
omits rollback or abort
omits audit semantics
changes public CLI or wheel behavior
changes version or release metadata
expands public claims
```

## Authorized Files

This gate may create or edit only:

```text
research/nesira_policy_profile/nesira_phase2_runner_action_class_taxonomy.md
research/nesira_policy_profile/nesira_phase2_runner_action_class_taxonomy_review.md
```

Any source, tests, workflow, pyproject, manifest, version, release, tag,
publication, public claim, CLI, runner, subprocess, filesystem mutation, or
network execution change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Next Step

If this taxonomy is accepted, the next gate remains docs-only:

```text
nesira_phase2_runner_side_effect_budget_model
```

That model must define the generic side-effect accounting rules before any
candidate class receives implementation authorization.
