import SpiraFormalCore.Action
import SpiraFormalCore.Contract
import SpiraFormalCore.Domain1.Evidence
import SpiraFormalCore.Domain1.Policy

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain1

def LegacyAction.toCoreAction : LegacyAction -> Action
  | LegacyAction.PROCEED => Action.PROCEED
  | LegacyAction.ASK_HUMAN => Action.REPORT_NOT_EVALUATED
  | LegacyAction.STOP_BLOCKED => Action.STOP_BLOCKED
  | LegacyAction.REPORT_NOT_EVALUATED => Action.REPORT_NOT_EVALUATED

def legacyStop : LegacyAction -> Bool
  | LegacyAction.PROCEED => false
  | LegacyAction.ASK_HUMAN => true
  | LegacyAction.STOP_BLOCKED => true
  | LegacyAction.REPORT_NOT_EVALUATED => true

def hasRequiredUnknown (evidence : PythonArtifactEvidence) : Bool :=
  !evidence.notEvaluatedItems.isEmpty

def hasBlockingStatus (evidence : PythonArtifactEvidence) : Bool :=
  evidence.worstClaimStatus == WorstClaimStatus.BLOCK

def formalLegacyAction (evidence : PythonArtifactEvidence) : LegacyAction :=
  evidence.legacyAction

def formalAction (evidence : PythonArtifactEvidence) : Action :=
  if hasBlockingStatus evidence then
    Action.STOP_BLOCKED
  else if hasRequiredUnknown evidence then
    Action.REPORT_NOT_EVALUATED
  else
    evidence.legacyAction.toCoreAction

def formalReasonCodes (evidence : PythonArtifactEvidence) : ExplicitList ReasonCode :=
  evidence.reasonCodes

def formalNotEvaluated (evidence : PythonArtifactEvidence) : ExplicitList NotEvaluatedItem :=
  evidence.notEvaluatedItems

def formalNotClaimed (evidence : PythonArtifactEvidence) : ExplicitList NotClaimedItem :=
  evidence.notClaimed

def formalEvidenceRefs (evidence : PythonArtifactEvidence) : ExplicitList EvidenceRef :=
  { items := [
      evidence.artifactIdentityRef,
      evidence.claimsIdentityRef,
      evidence.contextIdentityRef,
      evidence.decisionIdentityRef
    ] }

def formalProofRefs (evidence : PythonArtifactEvidence) : ExplicitList ProofRef :=
  { items := [
      evidence.compactReferenceRef,
      evidence.proofIdentityRef
    ] }

def formalContract (evidence : PythonArtifactEvidence) : MachineContract :=
  { domainId := domainId
    subjectId := evidence.subjectId
    policyId := (policy evidence.schemaVersion).policyId
    schemaVersion := evidence.schemaVersion
    producerId := evidence.producerId
    contractId := defaultContractId
    action := formalAction evidence
    stop := (formalAction evidence).stop
    reasonCodes := formalReasonCodes evidence
    blockingItems :=
      if formalAction evidence == Action.STOP_BLOCKED then
        ExplicitList.singleton "blocking_artifact_finding"
      else ExplicitList.empty
    notEvaluated := formalNotEvaluated evidence
    notClaimed := formalNotClaimed evidence
    evidenceRefs := formalEvidenceRefs evidence
    proofRefs := formalProofRefs evidence }

end Domain1
end SpiraFormalCore
