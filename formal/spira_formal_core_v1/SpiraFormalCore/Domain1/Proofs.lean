import SpiraFormalCore.Domain1.Decision

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain1

theorem ask_human_maps_to_report_not_evaluated :
    LegacyAction.toCoreAction LegacyAction.ASK_HUMAN = Action.REPORT_NOT_EVALUATED := by
  rfl

theorem legacy_stop_consistent (action : LegacyAction) :
    legacyStop action = action.toCoreAction.stop := by
  cases action <;> rfl

theorem block_status_prevents_proceed
    (evidence : PythonArtifactEvidence)
    (hBlock : evidence.worstClaimStatus = WorstClaimStatus.BLOCK) :
    formalAction evidence != Action.PROCEED := by
  simp [formalAction, hasBlockingStatus, hBlock]

theorem required_unknown_prevents_silent_pass
    (evidence : PythonArtifactEvidence)
    (hBlock : evidence.worstClaimStatus != WorstClaimStatus.BLOCK)
    (hUnknown : evidence.notEvaluatedItems.isEmpty = false) :
    formalAction evidence != Action.PROCEED := by
  cases hStatus : evidence.worstClaimStatus <;>
    simp [formalAction, hasBlockingStatus, hasRequiredUnknown, hStatus, hUnknown] at *

theorem explicit_reason_codes_preserved
    (evidence : PythonArtifactEvidence) :
    formalReasonCodes evidence = evidence.reasonCodes := by
  rfl

theorem explicit_not_evaluated_preserved
    (evidence : PythonArtifactEvidence) :
    formalNotEvaluated evidence = evidence.notEvaluatedItems := by
  rfl

theorem not_claimed_boundaries_preserved
    (evidence : PythonArtifactEvidence) :
    formalNotClaimed evidence = evidence.notClaimed := by
  rfl

theorem artifact_identity_preserved
    (evidence : PythonArtifactEvidence) :
    (formalEvidenceRefs evidence).items.head? = some evidence.artifactIdentityRef := by
  rfl

theorem proof_identity_preserved
    (evidence : PythonArtifactEvidence) :
    (formalProofRefs evidence).items.getLast? = some evidence.proofIdentityRef := by
  rfl

theorem contract_stop_consistent
    (evidence : PythonArtifactEvidence) :
    (formalContract evidence).stop = (formalContract evidence).action.stop := by
  rfl

end Domain1
end SpiraFormalCore
