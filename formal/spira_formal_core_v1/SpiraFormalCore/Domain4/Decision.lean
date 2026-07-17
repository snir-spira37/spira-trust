import SpiraFormalCore.Domain4.Policy

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain4

inductive ValidationStatus where
  | VALID_STRUCTURAL_ONLY
  | INVALID
  | RERUN_REQUIRED
  | NOT_EVALUATED
  | TOOL_ERROR
  deriving Repr, DecidableEq

inductive Phase1Action where
  | REPORT_NOT_EVALUATED
  | STOP_BLOCKED
  | RERUN_REQUIRED
  deriving Repr, DecidableEq

structure MachineContract where
  status : ValidationStatus
  action : Phase1Action
  stop : Bool
  artifactKind : ArtifactKind
  policyId : String
  schemaVersion : String
  deriving Repr, DecidableEq

def ValidationStatus.asString : ValidationStatus -> String
  | ValidationStatus.VALID_STRUCTURAL_ONLY => "VALID_STRUCTURAL_ONLY"
  | ValidationStatus.INVALID => "INVALID"
  | ValidationStatus.RERUN_REQUIRED => "RERUN_REQUIRED"
  | ValidationStatus.NOT_EVALUATED => "NOT_EVALUATED"
  | ValidationStatus.TOOL_ERROR => "TOOL_ERROR"

def Phase1Action.asString : Phase1Action -> String
  | Phase1Action.REPORT_NOT_EVALUATED => "REPORT_NOT_EVALUATED"
  | Phase1Action.STOP_BLOCKED => "STOP_BLOCKED"
  | Phase1Action.RERUN_REQUIRED => "RERUN_REQUIRED"

def actionOf : ValidationStatus -> Phase1Action
  | ValidationStatus.VALID_STRUCTURAL_ONLY => Phase1Action.REPORT_NOT_EVALUATED
  | ValidationStatus.INVALID => Phase1Action.STOP_BLOCKED
  | ValidationStatus.RERUN_REQUIRED => Phase1Action.RERUN_REQUIRED
  | ValidationStatus.NOT_EVALUATED => Phase1Action.REPORT_NOT_EVALUATED
  | ValidationStatus.TOOL_ERROR => Phase1Action.STOP_BLOCKED

def contractOf (kind : ArtifactKind) (policy : Policy) (status : ValidationStatus) : MachineContract :=
  { status := status
    action := actionOf status
    stop := true
    artifactKind := kind
    policyId := policy.policyId
    schemaVersion := policy.schemaVersion }

def severanceStatus (tuple : OutcomeTuple) : ValidationStatus :=
  match tuple.schema with
  | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION => ValidationStatus.RERUN_REQUIRED
  | SchemaOutcome.SCHEMA_STRUCTURAL_VIOLATION => ValidationStatus.INVALID
  | SchemaOutcome.SCHEMA_OK =>
      match tuple.context with
      | ContextOutcome.CONTEXT_EXPECTED_MISSING => ValidationStatus.NOT_EVALUATED
      | ContextOutcome.CONTEXT_MISMATCH => ValidationStatus.RERUN_REQUIRED
      | ContextOutcome.CONTEXT_OK =>
          match tuple.temporal with
          | TemporalOutcome.TEMPORAL_VIOLATION => ValidationStatus.RERUN_REQUIRED
          | TemporalOutcome.TEMPORAL_OK => ValidationStatus.VALID_STRUCTURAL_ONLY
          | TemporalOutcome.TEMPORAL_NOT_APPLICABLE => ValidationStatus.VALID_STRUCTURAL_ONLY

def isolationStatus (tuple : OutcomeTuple) : ValidationStatus :=
  match tuple.schema with
  | SchemaOutcome.SCHEMA_STRUCTURAL_VIOLATION => ValidationStatus.INVALID
  | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION => ValidationStatus.RERUN_REQUIRED
  | SchemaOutcome.SCHEMA_OK =>
      match tuple.context with
      | ContextOutcome.CONTEXT_MISMATCH => ValidationStatus.RERUN_REQUIRED
      | ContextOutcome.CONTEXT_EXPECTED_MISSING => ValidationStatus.NOT_EVALUATED
      | ContextOutcome.CONTEXT_OK =>
          match tuple.path with
          | PathOutcome.PATH_UNSAFE => ValidationStatus.INVALID
          | PathOutcome.PATH_OK | PathOutcome.PATH_NOT_APPLICABLE =>
              match tuple.evidence with
              | EvidencePresenceOutcome.EVIDENCE_MISSING => ValidationStatus.NOT_EVALUATED
              | EvidencePresenceOutcome.EVIDENCE_OK | EvidencePresenceOutcome.EVIDENCE_NOT_APPLICABLE =>
                  match tuple.symlink with
                  | SymlinkOutcome.SYMLINK_ESCAPE => ValidationStatus.INVALID
                  | SymlinkOutcome.SYMLINK_OK | SymlinkOutcome.SYMLINK_NOT_APPLICABLE =>
                      match tuple.directory with
                      | DirectoryEvidenceOutcome.DIR_AS_FILE => ValidationStatus.INVALID
                      | DirectoryEvidenceOutcome.DIR_OK | DirectoryEvidenceOutcome.DIR_NOT_APPLICABLE =>
                          match tuple.duplicate with
                          | DuplicateOutcome.DUP_PRESENT => ValidationStatus.INVALID
                          | DuplicateOutcome.DUP_OK | DuplicateOutcome.DUP_NOT_APPLICABLE =>
                              match tuple.hash with
                              | HashOutcome.HASH_MISMATCH => ValidationStatus.INVALID
                              | HashOutcome.HASH_OK | HashOutcome.HASH_NOT_APPLICABLE =>
                                  ValidationStatus.VALID_STRUCTURAL_ONLY

def statusOf (kind : ArtifactKind) (execMeta : ExecutionMeta) (tuple : OutcomeTuple) : ValidationStatus :=
  match execMeta with
  | ExecutionMeta.TOOL_ERROR => ValidationStatus.TOOL_ERROR
  | ExecutionMeta.INPUT_MALFORMED => ValidationStatus.RERUN_REQUIRED
  | ExecutionMeta.PARSED_OK =>
      match kind with
      | ArtifactKind.SEVERANCE_AUTHORIZATION => severanceStatus tuple
      | ArtifactKind.LEGACY_ISOLATION_RESULT => isolationStatus tuple

def NesiraCoreV2
    (kind : ArtifactKind)
    (execMeta : ExecutionMeta)
    (tuple : OutcomeTuple)
    (policy : Policy) : MachineContract :=
  contractOf kind policy (statusOf kind execMeta tuple)

end Domain4
end SpiraFormalCore
