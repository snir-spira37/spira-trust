# Nesira Phase 2 Runner Action Class Taxonomy

## Status

```text
DOCUMENT_TYPE: RESEARCH -- RUNNER ACTION CLASS TAXONOMY
PHASE: PHASE_2_RUNNER_ACTION_CLASS_TAXONOMY_GATE
SCOPE: TAXONOMY_ONLY
TAXONOMY_ID: SPIRA_NESIRA_PHASE2_RUNNER_ACTION_CLASS_TAXONOMY_V3
TAXONOMY_VERSION: 3
REVISION: authorize AUDIT_RECORD_APPEND_ONLY for one private declared sink append implementation gate

AUTHORIZES:
runner action-class taxonomy
ineligible action-class list
candidate future action-class vocabulary
eligible future implementation-authorization vocabulary
future side-effect-budget requirements

RUNNER_IMPLEMENTATION_BY_THIS_TAXONOMY: NOT_AUTHORIZED
RUNNER_IMPLEMENTATION: AUTHORIZED_ONLY_BY_CLASS_IMPLEMENTATION_AUTHORIZATION
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

This taxonomy names which action classes are categorically ineligible, which
classes may be considered by later docs-only gates, and which classes have a
separate implementation authorization. It does not itself implement runner
code.

## Core Lock

```text
AUTHORIZED_RUNNER_ACTION_CLASSES_NOW = [AUDIT_RECORD_APPEND_ONLY]
```

No action class is authorized for implementation by this taxonomy alone.
`AUDIT_RECORD_APPEND_ONLY` is authorized only by its separate implementation
authorization and only inside that authorization's exact envelope.

The purpose of this taxonomy is to prevent a runner from becoming a generic
execution surface while keeping the source of truth for class status in one
place.

## Classification Vocabulary

Every proposed runner action class must be classified as exactly one:

```text
INELIGIBLE_ALWAYS
CANDIDATE_FOR_FUTURE_MODEL_ONLY
ELIGIBLE_FOR_SEPARATE_IMPLEMENTATION_AUTHORIZATION
AUTHORIZED_NOW
```

For this document:

```text
AUTHORIZED_NOW contains only AUDIT_RECORD_APPEND_ONLY.
```

`CANDIDATE_FOR_FUTURE_MODEL_ONLY` means only that a later gate may write a
model for that class. It does not permit code.

`ELIGIBLE_FOR_SEPARATE_IMPLEMENTATION_AUTHORIZATION` means only that the class
has passed candidate modeling, side-effect budget modeling, and runner scope
revision review. It permits a later gate to draft an implementation
authorization for that exact class. It does not permit code.

`AUTHORIZED_NOW` means a class has received a separate implementation
authorization and may be implemented within that later gate's exact envelope.
It does not mean public exposure, release, CLI invocation, generic runner
behavior, or permission for any other class.

No document other than this taxonomy may introduce a new runner action-class
status. If a later gate needs a new status, this taxonomy must be revised first.

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
`CANDIDATE_FOR_FUTURE_MODEL_ONLY`,
`ELIGIBLE_FOR_SEPARATE_IMPLEMENTATION_AUTHORIZATION`, or `AUTHORIZED_NOW`
requires:

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

## Eligible For Separate Implementation Authorization

The following action classes are eligible for a later implementation
authorization discussion but not yet authorized:

```text
none
```

Eligibility does not move a class to `AUTHORIZED_NOW`.

## Authorized Now

The following action classes are authorized for implementation only within
their separate implementation gate envelope:

```text
AUDIT_RECORD_APPEND_ONLY
  status: AUTHORIZED_NOW
  authorization_source: nesira_phase2_audit_append_runner_implementation_authorization.md
  public_exposure: NOT_AUTHORIZED
  release: NOT_AUTHORIZED
  maximum implementation envelope:
    effect_shape: APPEND_ONE_BOUNDED_RECORD
    effect_count: 1
    total_effect_count: 1
    retry_count: 0
    supporting_effects: none
    sink_access: declared append capability only
```

`AUTHORIZED_NOW` for this class permits only private implementation under the
authorization source. It does not authorize public wheel exposure or release.

## Candidate Classes For Future Models Only

These classes may be modeled later, but are not authorized now:

```text
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

## Canonical Classification Table

This table is the source of truth for Phase 2 runner action-class status:

```text
GENERIC_SHELL_COMMAND                         INELIGIBLE_ALWAYS
GENERIC_SUBPROCESS                            INELIGIBLE_ALWAYS
GENERIC_SCRIPT_RUNNER                         INELIGIBLE_ALWAYS
GENERIC_PYTHON_MODULE_RUNNER                  INELIGIBLE_ALWAYS
GENERIC_FILESYSTEM_MUTATOR                    INELIGIBLE_ALWAYS
GENERIC_NETWORK_CLIENT                        INELIGIBLE_ALWAYS
ARBITRARY_COMMAND_EXECUTOR                    INELIGIBLE_ALWAYS
ARBITRARY_PATH_WRITE                          INELIGIBLE_ALWAYS
ARBITRARY_PATH_DELETE                         INELIGIBLE_ALWAYS
ARBITRARY_NETWORK_TARGET                      INELIGIBLE_ALWAYS
LIVE_ISOLATION_RUNNER                         INELIGIBLE_ALWAYS
SEVERANCE_EXECUTOR                            INELIGIBLE_ALWAYS
AUTOMATIC_REMEDIATOR                          INELIGIBLE_ALWAYS
SECRET_EXFILTRATION_PRONE_ACTION              INELIGIBLE_ALWAYS
UNBOUNDED_CLEANUP_ACTION                      INELIGIBLE_ALWAYS
SELF_MODIFYING_RUNNER                         INELIGIBLE_ALWAYS

AUDIT_RECORD_APPEND_ONLY                      AUTHORIZED_NOW

LOCAL_STATUS_MARKER_CREATE_ONLY               CANDIDATE_FOR_FUTURE_MODEL_ONLY
MANUAL_REVIEW_PACKET_MATERIALIZE_ONLY         CANDIDATE_FOR_FUTURE_MODEL_ONLY
ROLLBACK_ABORT_SIGNAL_REQUEST_ONLY            CANDIDATE_FOR_FUTURE_MODEL_ONLY
```

Any status not listed here is invalid.

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
declares ELIGIBLE_FOR_SEPARATE_IMPLEMENTATION_AUTHORIZATION outside this taxonomy
moves a class to ELIGIBLE without accepted candidate model, budget model,
non-executing evaluator, and runner scope revision
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
