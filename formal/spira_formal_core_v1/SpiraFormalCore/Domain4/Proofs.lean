import SpiraFormalCore.Domain4.Decision

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain4

theorem tool_error_stops
    (kind : ArtifactKind)
    (tuple : OutcomeTuple)
    (policy : Policy) :
    (NesiraCoreV2 kind ExecutionMeta.TOOL_ERROR tuple policy).action =
      Phase1Action.STOP_BLOCKED := by
  simp [NesiraCoreV2, statusOf, contractOf, actionOf]

theorem input_malformed_rerun
    (kind : ArtifactKind)
    (tuple : OutcomeTuple)
    (policy : Policy) :
    (NesiraCoreV2 kind ExecutionMeta.INPUT_MALFORMED tuple policy).action =
      Phase1Action.RERUN_REQUIRED := by
  simp [NesiraCoreV2, statusOf, contractOf, actionOf]

theorem schema_structural_violation_not_valid
    (kind : ArtifactKind)
    (tuple : OutcomeTuple)
    (policy : Policy)
    (hSchema : tuple.schema = SchemaOutcome.SCHEMA_STRUCTURAL_VIOLATION) :
    (NesiraCoreV2 kind ExecutionMeta.PARSED_OK tuple policy).action =
      Phase1Action.STOP_BLOCKED := by
  cases kind <;> simp [NesiraCoreV2, statusOf, severanceStatus, isolationStatus,
    contractOf, actionOf, hSchema]

theorem hash_mismatch_not_valid
    (tuple : OutcomeTuple)
    (policy : Policy)
    (hSchema : tuple.schema = SchemaOutcome.SCHEMA_OK)
    (hContext : tuple.context = ContextOutcome.CONTEXT_OK)
    (hPath : tuple.path = PathOutcome.PATH_OK)
    (hEvidence : tuple.evidence = EvidencePresenceOutcome.EVIDENCE_OK)
    (hSymlink : tuple.symlink = SymlinkOutcome.SYMLINK_OK)
    (hDirectory : tuple.directory = DirectoryEvidenceOutcome.DIR_OK)
    (hDuplicate : tuple.duplicate = DuplicateOutcome.DUP_OK)
    (hHash : tuple.hash = HashOutcome.HASH_MISMATCH) :
    (NesiraCoreV2 ArtifactKind.LEGACY_ISOLATION_RESULT ExecutionMeta.PARSED_OK tuple policy).action =
      Phase1Action.STOP_BLOCKED := by
  simp [NesiraCoreV2, statusOf, isolationStatus, contractOf, actionOf,
    hSchema, hContext, hPath, hEvidence, hSymlink, hDirectory, hDuplicate, hHash]

theorem unsafe_path_not_valid
    (tuple : OutcomeTuple)
    (policy : Policy)
    (hSchema : tuple.schema = SchemaOutcome.SCHEMA_OK)
    (hContext : tuple.context = ContextOutcome.CONTEXT_OK)
    (hPath : tuple.path = PathOutcome.PATH_UNSAFE) :
    (NesiraCoreV2 ArtifactKind.LEGACY_ISOLATION_RESULT ExecutionMeta.PARSED_OK tuple policy).action =
      Phase1Action.STOP_BLOCKED := by
  simp [NesiraCoreV2, statusOf, isolationStatus, contractOf, actionOf,
    hSchema, hContext, hPath]

theorem missing_evidence_not_evaluated
    (tuple : OutcomeTuple)
    (policy : Policy)
    (hSchema : tuple.schema = SchemaOutcome.SCHEMA_OK)
    (hContext : tuple.context = ContextOutcome.CONTEXT_OK)
    (hPath : tuple.path = PathOutcome.PATH_OK)
    (hEvidence : tuple.evidence = EvidencePresenceOutcome.EVIDENCE_MISSING) :
    (NesiraCoreV2 ArtifactKind.LEGACY_ISOLATION_RESULT ExecutionMeta.PARSED_OK tuple policy).action =
      Phase1Action.REPORT_NOT_EVALUATED := by
  simp [NesiraCoreV2, statusOf, isolationStatus, contractOf, actionOf,
    hSchema, hContext, hPath, hEvidence]

theorem context_expected_missing_not_evaluated
    (kind : ArtifactKind)
    (tuple : OutcomeTuple)
    (policy : Policy)
    (hSchema : tuple.schema = SchemaOutcome.SCHEMA_OK)
    (hContext : tuple.context = ContextOutcome.CONTEXT_EXPECTED_MISSING) :
    (NesiraCoreV2 kind ExecutionMeta.PARSED_OK tuple policy).action =
      Phase1Action.REPORT_NOT_EVALUATED := by
  cases kind <;> simp [NesiraCoreV2, statusOf, severanceStatus, isolationStatus,
    contractOf, actionOf, hSchema, hContext]

theorem core_deterministic
    (kind : ArtifactKind)
    (execMeta : ExecutionMeta)
    (tuple : OutcomeTuple)
    (policy : Policy) :
    NesiraCoreV2 kind execMeta tuple policy = NesiraCoreV2 kind execMeta tuple policy := by
  rfl

theorem stop_true
    (kind : ArtifactKind)
    (execMeta : ExecutionMeta)
    (tuple : OutcomeTuple)
    (policy : Policy) :
    (NesiraCoreV2 kind execMeta tuple policy).stop = true := by
  simp [NesiraCoreV2, contractOf]

end Domain4
end SpiraFormalCore
